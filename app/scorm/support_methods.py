import time
from datetime import datetime, timedelta

import rustici_software_cloud_v2 as scorm_cloud
from rustici_software_cloud_v2.models import ImportFetchRequestSchema
from rustici_software_cloud_v2.rest import ApiException as ScormCloudApiException

import GEN.settings
from django.contrib import messages
from django.contrib.auth.models import User

# ScormCloud API credentials
# Note: These are not the same credentials used to log in to ScormCloud
app_id = GEN.settings.SCORM_CLOUD_APP_ID
secret_key = GEN.settings.SCORM_CLOUD_SECRET_KEY
instance_name = GEN.settings.INSTANCE_NAME

# Configure HTTP basic authorization: APP_NORMAL
config = scorm_cloud.Configuration()
config.username = app_id
config.password = secret_key


def initialize_scorm_cloud():
    """
    Set the default configuration values for new Scorm Cloud configuration object.

    Returns: ScormCloud API instance.

    """

    scorm_cloud.Configuration().set_default(config)
    sc = ScormCloud_Api()
    return sc


def export_to_scorm_cloud(scorm_object, request):
    """
    Export SCORM zip package into ScormCloud.

    Args:
        request: Django HttpRequest (object).
        scorm_object: GEN ScormPackage (object).

    """

    # Note: ScormCloud uses the terms 'packages' and 'courses' interchangeably, but
    # prefers to use 'courses'. Within the context of SCORM packages, they will be
    # called 'courses' (but are not to be confused with GEN Courses/Modules).

    # TODO: test without S3
    if GEN.settings.USE_S3:
        course_path = scorm_object.file.url
        course_id = f"{instance_name}-object_{scorm_object.id}"
    else:
        course_path = scorm_object.file.path
        course_id = f"{instance_name}-object_{scorm_object.id}"

    sc = initialize_scorm_cloud()

    # Create a course
    try:
        if GEN.settings.USE_S3:
            # create course based on media file URL
            course_details = sc.upload_course(course_id, course_path)
        else:
            # create course using local file
            course_details = sc.create_course(course_id, course_path)

        # Show details of the newly imported course
        print("Newly Imported Course Details: ")
        print(course_details)

    except (scorm_cloud.rest.ApiException, ValueError) as err:
        # raise ScormCloudApiException(f"Failed to export package into ScormCloud: {err}")
        messages.error(request, f"Action failed: {err}.", extra_tags="error")

    scorm_object.package_id = course_id
    scorm_object.save(update_fields=["package_id"])


def delete_from_scorm_cloud(scorm_object):
    """
    This will delete the SCORM package from ScormCloud, and all related registrations.

    Args:
        scorm_object: GEN ScormPackage (object)..

    """

    sc = initialize_scorm_cloud()

    # Delete ScormCloud package/course and all relate registrations.
    sc.delete_course(scorm_object.package_id)


def delete_registration_from_scorm_cloud(registration_object):
    """
    Delete registration from ScormCloud based on GEN ScormRegistration object.

    Args:
        registration_object: GEN ScormRegistration (object).

    """

    sc = initialize_scorm_cloud()

    # Delete single registration
    sc.delete_registration(registration_object.registration_id)


def enroll_learners(scorm_object):
    # TODO: temporary code: this should be done to ALL of the course/module learners
    learner = User.objects.get(pk=1)

    enroll_learner_to_scorm_cloud_package(scorm_object, learner)


def generate_launch_url(scorm_object, learner, redirect_on_exit_url):
    """
    Generate the ScormCloud URL that allows the learner to access the SCORM package.

    Args:
        scorm_object: GEN ScormPackage (object).
        learner: User (object).
        redirect_on_exit_url: URL (string).

    Returns: ScormCloud launch URL (string).

    """

    sc = initialize_scorm_cloud()

    # check if registration_object exists locally
    from scorm.models import ScormRegistration

    try:
        registration_object = ScormRegistration.objects.get(
            package_object=scorm_object, learner=learner
        )
    except ScormRegistration.DoesNotExist:
        # registration does not exist, creating one
        registration_object = enroll_learner_to_scorm_cloud_package(
            scorm_object, learner
        )

    if registration_object:
        launch_link = sc.build_launch_link(
            registration_object.registration_id,
            redirect_on_exit_url=redirect_on_exit_url,
        )
    else:
        launch_link = None

    return launch_link


def enroll_learner_to_scorm_cloud_package(scorm_object, learner):
    """
    Enroll the learner to a ScormCloud package/course (create a registration).
    First it checks if a ScormCloud registration exists, and creates one if it doesn't.
    After, it creates a GEN ScormRegistration object which links the ScormCloud
    registration to the GEN user.

    Args:
        scorm_object: GEN ScormPackage (object).
        learner: User (object).

    Returns: GEN ScormRegistration (object).

    """

    scorm_cloud_package_id = f"{instance_name}-object_{scorm_object.id}"
    scorm_cloud_learner_id = f"{instance_name}-learner_{learner.id}"
    scorm_cloud_registration_id = (
        f"{instance_name}-object_{scorm_object.id}-learner_{learner.id}"
    )

    sc = initialize_scorm_cloud()

    # Check if registration already exists on ScormCloud
    scorm_cloud_registration_exists = sc.check_registration(scorm_cloud_registration_id)

    # Create registration if it doesn't exist
    if not scorm_cloud_registration_exists:
        try:
            # Create a registration
            sc.create_registration(
                scorm_cloud_package_id,
                scorm_cloud_learner_id,
                scorm_cloud_registration_id,
            )

        except (scorm_cloud.rest.ApiException, ValueError) as err:
            raise ScormCloudApiException(
                status=err.status,
                reason=f"{err.reason}\nHTTP response headers: {err.headers}\nHTTP response body: {err.body}\n",
            )

    # Create registration object on GEN
    registration_object = scorm_object.create_registration(
        registration_id=scorm_cloud_registration_id, learner=learner
    )

    return registration_object


def get_registration_details(registration_object):
    """
    Obtains details about a ScormCloud registration, which includes activity completion,
    attempts, score, etc.

    Args:
        registration_object: GEN ScormRegistration (object).

    Returns: ScormCloud registration details (RegistrationSchema object).

    """

    sc = initialize_scorm_cloud()

    result = sc.get_result_for_registration(registration_object.registration_id)

    return result


class ScormCloud_Api:

    # Based on sample code from https://github.com/RusticiSoftware/scormcloud-api-v2-client-python

    def __configure_oauth(self, scopes):
        """
        Sets the default OAuth token passed with all calls to the API.

        If a token is created with limited scope (i.e. read:registration),
        calls that require a different permission set will error. Either a
        new token needs to be generated with the correct scope, or the
        default access token can be reset to None. This would cause the
        request to be made with basic auth credentials (appId/ secret key)
        instead.

        Additionally, you could create a new configuration object and set
        the token on that object instead of the default access token. This
        configuration would then be passed into the Api object:

        config = scorm_cloud.Configuration()
        token_request = {
            'permissions': scorm_cloud.PermissionsSchema([ "write:course", "read:course" ]),
            'expiry': (datetime.utcnow() + timedelta(minutes=2)).isoformat() + 'Z'
        }
        config.access_token = app_management_api.create_token(token_request).result
        course_api = scorm_cloud.CourseApi(scorm_cloud.ApiClient(config))

        Any calls that would use this CourseApi instance would then have the
        write:course and read:course permissions passed automatically, but
        other instances would be unaffected and continue to use other means
        of authorization.

        :param scopes: List of permissions for calls made with the token.
        :type scopes: list[str]
        """

        app_management_api = scorm_cloud.ApplicationManagementApi()

        # Set permissions and expiry time of the token
        # The expiry expected for token request must be in ISO-8601 format
        expiry = (datetime.utcnow() + timedelta(minutes=2)).isoformat() + "Z"
        permissions = scorm_cloud.PermissionsSchema(scopes)

        # Make the request to get the OAuth token
        token_request = scorm_cloud.TokenRequestSchema(permissions, expiry)
        token_result = app_management_api.create_token(token_request)

        # Set the default access token used with further API requests.
        # To remove the token, reset config.access_token back to None
        # and set the default before the next call.
        config = scorm_cloud.Configuration()
        config.access_token = token_result.result
        scorm_cloud.Configuration().set_default(config)

    def upload_course(self, course_id, file_url):
        # This call will use OAuth with the "write:course" scope
        # if configured.  Otherwise the basic auth credentials will be used
        course_api = scorm_cloud.CourseApi()
        import_request = ImportFetchRequestSchema(url=file_url)
        job_id = course_api.create_fetch_and_import_course_job(
            course_id, import_request=import_request
        )

        # This call will use OAuth with the "read:course" scope
        # if configured.  Otherwise the basic auth credentials will be used
        job_result = course_api.get_import_job_status(job_id.result)
        while job_result.status == "RUNNING":
            time.sleep(5)
            job_result = course_api.get_import_job_status(job_id.result)

        if job_result.status == "ERROR":
            raise ValueError(
                "Error uploading and importing course into ScormCloud: "
                + job_result.message
            )

        return job_result.import_result.course

    def create_course(self, course_id, course_path):
        """
        Creates a course by uploading the course from your local machine.
        Courses are a package of content for a learner to consume.

        Other methods for importing a course exist. Check the documentation
        for additional ways of importing a course.

        :param course_id: Id that will be used to identify the course.
        :type course_id: str
        :param course_path: Path to the course being uploaded.
        :type course_path: str
        :returns: Detailed information about the newly uploaded course.
        :rtype: CourseSchema
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "write:course", "read:course" ])

        # This call will use OAuth with the "write:course" scope
        # if configured.  Otherwise the basic auth credentials will be used
        course_api = scorm_cloud.CourseApi()
        job_id = course_api.create_upload_and_import_course_job(
            course_id, file=course_path
        )

        # This call will use OAuth with the "read:course" scope
        # if configured.  Otherwise the basic auth credentials will be used
        job_result = course_api.get_import_job_status(job_id.result)
        while job_result.status == "RUNNING":
            time.sleep(1)
            job_result = course_api.get_import_job_status(job_id.result)

        if job_result.status == "ERROR":
            raise ValueError("Course is not properly formatted: " + job_result.message)

        return job_result.import_result.course

    def create_registration(self, course_id, learner_id, registration_id):
        """
        Creates a registration allowing the learner to consume the course
        content. A registration is the link between a learner and a single
        course.

        :param course_id: Id of the course to register the learner for.
        :type course_id: str
        :param learner_id: Id that will be used to identify the learner.
        :type learner_id: str
        :param registration_id: Id that will be used to identify the registration.
        :type registration_id: str
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "write:registration" ])

        registration_api = scorm_cloud.RegistrationApi()
        learner = scorm_cloud.LearnerSchema(learner_id)
        registration = scorm_cloud.CreateRegistrationSchema(
            course_id, learner, registration_id
        )
        registration_api.create_registration(registration)

    def build_launch_link(self, registration_id, redirect_on_exit_url):
        """
        Builds a url allowing the learner to access the course.

        :param registration_id: Id of the registration the link is being built for.
        :type registration_id: str
        :returns: Link for the learner to launch the course.
        :rtype: str
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "read:registration" ])

        registration_api = scorm_cloud.RegistrationApi()
        settings = scorm_cloud.LaunchLinkRequestSchema(
            redirect_on_exit_url=redirect_on_exit_url
        )
        launch_link = registration_api.build_registration_launch_link(
            registration_id, settings
        )

        return launch_link.launch_link

    def get_result_for_registration(self, registration_id):
        """
        Gets information about the progress of the registration.

        For the most up-to-date results, you should implement our postback
        mechanism. The basic premise is that any update to the registration
        would cause us to send the updated results to your system.

        More details can be found in the documentation:
        https://cloud.scorm.com/docs/v2/guides/postback/

        :param registration_id: Id of the registration to get results for.
        :type registration_id: str
        :returns: Detailed information about the registration's progress.
        :rtype: RegistrationSchema
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "read:registration" ])

        registration_api = scorm_cloud.RegistrationApi()
        progress = registration_api.get_registration_progress(registration_id)

        return progress

    def get_all_courses(self):
        """
        Gets information about all courses. The result received from the API
        call is a paginated list, meaning that additional calls are required
        to retrieve all the information from the API.

        :returns: List of detailed information about all of the courses.
        :rtype: list[CourseSchema]
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "read:course" ])

        # Additional filters can be provided to this call to get a subset
        # of all courses.
        course_api = scorm_cloud.CourseApi()
        response = course_api.get_courses()

        # This call is paginated, with a token provided if more results exist
        course_list = response.courses
        while response.more is not None:
            response = course_api.get_courses(more=response.more)
            course_list += response.courses

        return course_list

    def get_all_registrations(self):
        """
        Gets information about the registration progress for all
        registrations. The result received from the API call is a paginated
        list, meaning that additional calls are required to retrieve all the
        information from the API.

        This call can be quite time-consuming and tedious with lots of
        registrations. If you find yourself making lots of calls to this
        endpoint, it might be worthwhile to look into registration postbacks.

        More details can be found in the documentation:
        https://cloud.scorm.com/docs/v2/guides/postback/

        :returns: List of detailed information about all of the registrations.
        :rtype: list[RegistrationSchema]
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "read:registration" ])

        # Additional filters can be provided to this call to get a subset
        # of all registrations.
        registration_api = scorm_cloud.RegistrationApi()
        response = registration_api.get_registrations()

        # This call is paginated, with a token provided if more results exist
        registration_list = response.registrations
        while response.more is not None:
            response = registration_api.get_registrations(more=response.more)
            registration_list += response.registrations

        return registration_list

    def clean_up(self, course_id, registration_id):
        """
        Deletes all of the data generated by this sample.
        This code is run even if the program has errored out, providing a
        "clean slate" for every run of this sample.

        It is not necessary to delete registrations if the course
        they belong to has been deleted. Deleting the course will
        automatically queue deletion of all registrations associated with
        the course. There will be a delay between when the course is deleted
        and when the registrations for the course have been removed. The
        registration deletion has been handled here to prevent scenarios
        where the registration hasn't been deleted yet by the time the
        sample has been rerun.

        :param course_id: Id of the course to delete.
        :type course_id: str
        :param registration_id: Id of the registration to delete.
        :type registration_id: str
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "delete:course", "delete:registration" ])

        # This call will use OAuth with the "delete:course" scope
        # if configured.  Otherwise the basic auth credentials will be used
        course_api = scorm_cloud.CourseApi()
        course_api.delete_course(course_id)

        # The code below is to prevent race conditions if the
        # sample is run in quick successions.

        # This call will use OAuth with the "delete:registration" scope
        # if configured.  Otherwise the basic auth credentials will be used
        registration_api = scorm_cloud.RegistrationApi()
        registration_api.delete_registration(registration_id)

    def delete_course(self, course_id):
        """
        Deletes a package/course from ScormCloud.

        Note: It is not necessary to delete registrations if the course
        they belong has been deleted. Deleting the course will
        automatically queue deletion of all registrations associated with
        the course. There will be a delay between when the course is deleted
        and when the registrations for the course have been removed.

        :param course_id: Id of the course to delete.
        :type course_id: str
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "delete:course", "delete:registration" ])

        # This call will use OAuth with the "delete:course" scope
        # if configured.  Otherwise the basic auth credentials will be used
        course_api = scorm_cloud.CourseApi()
        try:
            course_api.delete_course(course_id)
        except (ScormCloudApiException, ValueError) as err:
            raise ScormCloudApiException(f"Failed to delete SCORM package: {err}")

    def delete_registration(self, registration_id):
        """
        Deletes a registration from ScormCloud.

        Note: It is not necessary to delete registrations if the course
        they belong has been deleted. Deleting the course will
        automatically queue deletion of all registrations associated with
        the course. There will be a delay between when the course is deleted
        and when the registrations for the course have been removed.

        :param registration_id: Id of the registration to delete.
        :type registration_id: str
        """

        # (Optional) Further authenticate via OAuth token access
        # self.__configure_oauth([ "delete:course", "delete:registration" ])

        # This call will use OAuth with the "delete:registration" scope
        # if configured.  Otherwise the basic auth credentials will be used
        registration_api = scorm_cloud.RegistrationApi()
        registration_api.delete_registration(registration_id)

    def check_registration(self, registration_id):
        """
        Checks that the registration exists within SCORM Cloud.

        Args:
            registration_id: Id of the registration.

        Returns: Boolean value that represents if the registration exists.

        """

        # API documentation: https://cloud.scorm.com/docs/v2/reference/swagger/#/registration/GetRegistration
        registration_api = scorm_cloud.RegistrationApi()
        try:
            result = registration_api.get_registration_with_http_info(registration_id)
        except ScormCloudApiException as error:
            if error.status == 404:
                return False
            else:
                raise ScormCloudApiException(
                    status=error.status,
                    reason=f"{error.reason}\nHTTP response headers: {error.headers}\nHTTP response body: {error.body}\n",
                )

        # API returns code 200 if it exists, 404 for not found
        return result[1] == 200

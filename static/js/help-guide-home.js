const btn_next_text = gettext('Next');
const btn_prev_text = gettext('Back');
const btn_close_text = gettext('Close');

const tour = new Shepherd.Tour({
  defaultStepOptions: {
    cancelIcon: {
      enabled: true
    },
    classes: 'shadow-md',
    scrollTo: { behavior: 'smooth', block: 'center' }
  },
  useModalOverlay: true,
});

const steps = [
  {
    title: gettext('GEN Guide'),
    text: gettext('Welcome to GEN\'s help. This quick guide will briefly explain each area of GEN\'s interface.'),
    buttons: [
      {
        action: function() {
          return this.next();
        },
        text: btn_next_text
      }
    ],
    id: 'start'
  },
  {
    title: gettext('Top navigation bar'),
    text: gettext('In this area are located two elements: <b>Help</b> (which activated this guide) and <b>your username and avatar</b>, which gives access to your account info, change password, and logging out from GEN.'),
    attachTo: {
      element: '#main-navbar',
      on: 'bottom'
    },
    buttons: [
      {
        action: function() {
          return this.back();
        },
        secondary: true,
        text: btn_prev_text
      },
      {
        action: function() {
          return this.next();
        },
        text: btn_next_text
      }
    ],
    id: 'navbar-main'
  },
  {
    title: gettext('Page Name'),
    text: gettext('This area displays the current page name.'),
    attachTo: {
      element: '#page-name',
      on: 'auto'
    },
    buttons: [
      {
        action: function() {
          return this.back();
        },
        secondary: true,
        text: btn_prev_text
      },
      {
        action: function() {
          return this.next();
        },
        text: btn_next_text
      }
    ],
    id: 'course-name'
  },
  {
    title: gettext('Courses'),
    text: gettext('Here are listed the courses in which you are currently enrolled.'),
    attachTo: {
      element: '#courses',
      on: 'auto'
    },
    buttons: [
      {
        action: function() {
          return this.back();
        },
        secondary: true,
        text: btn_prev_text
      },
      {
        action: function() {
          return this.next();
        },
        text: btn_next_text
      }
    ],
    id: 'navbar-sections'
  },
  {
    title: gettext('Getting support'),
    text: gettext('If you need to get in touch in case of any questions or issues, please send an email to <a href="mailto:support@maxsimgen.com">support@maxsimgen.com</a>.<br><br>Thank you for using this guide, bye.'),
    buttons: [
      {
        action: function() {
          return this.back();
        },
        secondary: true,
        text: btn_prev_text
      },
      {
        action: function() {
          return this.complete();
        },
        text: btn_close_text
      }
    ],
    id: 'section-content'
  },
]

tour.addSteps(steps);

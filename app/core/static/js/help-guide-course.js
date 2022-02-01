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
    title: gettext('Course Name'),
    text: gettext('This area displays the current course/module name.'),
    attachTo: {
      element: '#course-name',
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
    title: gettext('Sections'),
    text: gettext('This interactable element allows you to navigate through the sections available in the current course/module. You should follow these sections in the order they are presented. If one of the sections has any requirements, it will also be shown here.'),
    attachTo: {
      element: '#sections-navbar',
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
    title: gettext('Section content'),
    text: gettext('This is the main content area, where the selected section data is displayed and most GEN interactions takes place.'),
    attachTo: {
      element: '#section-content',
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
    id: 'section-content'
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

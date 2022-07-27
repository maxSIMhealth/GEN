const btn_next_text = gettext('Next');
const btn_prev_text = gettext('Back');
const btn_close_text = gettext('Close');

const tour = new Shepherd.Tour({
    defaultStepOptions: {
        cancelIcon: {
            enabled: true
        },
        classes: 'shadow-md',
        scrollTo: {behavior: 'smooth', block: 'center'}
    },
    useModalOverlay: true,
});

const steps = [
    {
        id: 'start',
        title: gettext('GEN Guide'),
        text: gettext('Welcome to GEN\'s help. This quick guide will briefly explain each area of GEN\'s interface.'),
        buttons: [
            {
                action: function () {
                    return this.next();
                },
                text: btn_next_text
            }
        ]
    },
    {
        id: 'navbar-main',
        title: gettext('Top navigation bar'),
        text: gettext('In this area are located two elements: <b>Help</b> (which activated this guide) and <b>your username and avatar</b>, which gives access to your account info, change password, and logging out from GEN.'),
        attachTo: {
            element: '#main-navbar',
            on: 'bottom'
        },
        buttons: [
            {
                action: function () {
                    return this.back();
                },
                secondary: true,
                text: btn_prev_text
            },
            {
                action: function () {
                    return this.next();
                },
                text: btn_next_text
            }
        ]
    },
    {
        id: 'page-name',
        title: gettext('Page Name'),
        text: gettext('This area displays the current page name.'),
        attachTo: {
            element: '#page-name',
            on: 'auto'
        },
        buttons: [
            {
                action: function () {
                    return this.back();
                },
                secondary: true,
                text: btn_prev_text
            },
            {
                action: function () {
                    return this.next();
                },
                text: btn_next_text
            }
        ]
    },
    {
        id: 'help-content',
        title: gettext('Help'),
        text: gettext('Here are listed the frequently asked questions about GEN and its components.'),
        attachTo: {
            element: '#help-accordion',
            on: 'auto'
        },
        buttons: [
            {
                action: function () {
                    return this.back();
                },
                secondary: true,
                text: btn_prev_text
            },
            {
                action: function () {
                    return this.next();
                },
                text: btn_next_text
            }
        ]
    },
    {
    id: 'language-bar',
    title: gettext('Language'),
    text: gettext('And here you can choose which language you prefer using. You can change it at any moment.'),
    attachTo: {
      element: '#footer-language-selector',
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
    ]
  },
    {
        id: 'section-content',
        title: gettext('Getting support'),
        text: gettext('If you need to get in touch in case of any questions or issues, please send an email to <a href="mailto:support@maxsimgen.com">support@maxsimgen.com</a>.<br><br>Thank you for using this guide.'),
        buttons: [
            {
                action: function () {
                    return this.back();
                },
                secondary: true,
                text: btn_prev_text
            },
            {
                action: function () {
                    return this.complete();
                },
                text: btn_close_text
            }
        ]
    },
]

tour.addSteps(steps);

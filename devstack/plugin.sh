# plugin.sh - DevStack plugin.sh dispatch script watcher-dashboard

WATCHER_DASHBOARD_DIR=$(cd $(dirname $BASH_SOURCE)/.. && pwd)

function install_watcher_dashboard {
    setup_develop ${WATCHER_DASHBOARD_DIR}
}

function configure_watcher_dashboard {
    cp -a ${WATCHER_DASHBOARD_DIR}/watcher_dashboard/local/enabled/* ${DEST}/horizon/openstack_dashboard/local/enabled/
    cp -a ${WATCHER_DASHBOARD_DIR}/watcher_dashboard/conf/* ${DEST}/horizon/openstack_dashboard/conf/
}

function init_watcher_dashboard {
    # Setup alias for django-admin which could be different depending on distro
    python3 ${DEST}/horizon/manage.py collectstatic --noinput
    python3 ${DEST}/horizon/manage.py compress --force
}

# check for service enabled
if is_service_enabled watcher-dashboard; then

    if [[ "$1" == "stack" && "$2" == "pre-install"  ]]; then
        # Set up system services
        # no-op
        :

    elif [[ "$1" == "stack" && "$2" == "install"  ]]; then
        # Perform installation of service source
        echo_summary "Installing Watcher Dashboard"
        install_watcher_dashboard

    elif [[ "$1" == "stack" && "$2" == "post-config"  ]]; then
        # Configure after the other layer 1 and 2 services have been configured
        echo_summary "Configurng Watcher Dashboard"
        configure_watcher_dashboard
        init_watcher_dashboard

    elif [[ "$1" == "stack" && "$2" == "extra"  ]]; then
        # no-op
        :
    fi

    if [[ "$1" == "unstack"  ]]; then
        rm -f ${DEST}/horizon/openstack_dashboard/local/enabled/_310*
        rm -f ${DEST}/horizon/openstack_dashboard/conf/watcher*

    fi

    if [[ "$1" == "clean"  ]]; then
        # Remove state and transient data
        # Remember clean.sh first calls unstack.sh
        # no-op
        :
    fi
fi

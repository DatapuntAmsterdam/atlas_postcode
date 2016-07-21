#!groovy

def tryStep(String message, Closure block, Closure tearDown = null) {
    try {
        block();
    }
    catch (Throwable t) {
        slackSend message: "${env.JOB_NAME}: ${message} failure ${env.BUILD_URL}", channel: '#ci-channel', color: 'danger'

        throw t;
    }
    finally {
        if (tearDown) {
            tearDown();
        }
    }
}


node {

    stage "Checkout"
    checkout scm


    stage "Build base image"
    tryStep "build", {
        sh "docker-compose build"
    }


    stage 'Test'
    tryStep "test", {
        sh "docker exec \$(docker-compose ps -q postcode) /app/run_test.sh"
    }, {
        sh "docker-compose stop"
        sh "docker-compose rm -f"
    }

    stage "Build develop image"
    tryStep "build", {
        def image = docker.build("admin.datapunt.amsterdam.nl:5000/atlas/postcode:${env.BUILD_NUMBER}")
        image.push()
        image.push("develop")
    }
}

node {
    stage name: "Deploy to ACC", concurrency: 1
    tryStep "deployment", {
        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'acceptance'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-atlas-postcode.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                ]
    }
}


stage name: 'Waiting for approval'

input "Deploy to Production?"


node {
    stage 'Build production image'
    tryStep "image tagging", {
        def image = docker.image("admin.datapunt.amsterdam.nl:5000/atlas/postcode:${env.BUILD_NUMBER}")
        image.pull()

        image.push("master")
        image.push("latest")
    }
}

node {
    stage name: "Deploy to PROD", concurrency: 1
    tryStep "deployment", {
        build job: 'Subtask_Openstack_Playbook',
                parameters: [
                        [$class: 'StringParameterValue', name: 'INVENTORY', value: 'production'],
                        [$class: 'StringParameterValue', name: 'PLAYBOOK', value: 'deploy-atlas-postcode.yml'],
                        [$class: 'StringParameterValue', name: 'BRANCH', value: 'master'],
                ]
    }
}
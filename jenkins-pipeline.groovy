//TO CHANGE
//- environment details
//- THE SLACK DETAILS in send_slack_notification() & post job slack notifications details
//- API url and key in start_backup_server() & run_script_on_backup_server()
//- scriptname:'value' in required stages


pipeline {
    agent any

    parameters {
        choice(
            choices: ['Complete-Sync-&-Latest-Code-Update' , 'Only-Sync-Backup-Server-from-Prod-Server' , 'Only-Pull-Latest-Code-On-Backup-Server' , 'Only-Sync-Database-From-Production-To-Backup-Server' , 'Stop-The-Backup-Server' , 'Start-The-Backup-Server'],
            description: 'Select the job wanted to perform on the Backup Server',
            name: 'REQUESTED_ACTION')
    }

    environment {
        SSHUSERNAME = "ec2-username-example"
        SCRIPTPATH = "/home/path/to/script"
    }

    stages {
        stage('Complete-Sync-&-Latest-Code-Update') {
          when {
              expression { params.REQUESTED_ACTION == 'Complete-Sync-&-Latest-Code-Update' }
          }
          steps{
            script{
              send_slack_notification stagename: 'Complete-Sync-&-Latest-Code-Update'
              echo "===========================================\nRUNNING: ${params.REQUESTED_ACTION}\n==========================================="
              echo "==============================\nSTEP 1: Starting Backup Server\n=============================="
              start_backup_server()
              echo "===========================================================\nSTEP 2:Complete Sync of Backup Server & Latest Code Update\n==========================================================="
              run_script_on_backup_server scriptname: 'test.sh'
              echo "========================="
            }
          }
        }

        stage('Only-Sync-Backup-Server-from-Prod-Server') {
          when {
              expression { params.REQUESTED_ACTION == 'Only-Sync-Backup-Server-from-Prod-Server' }
          }
          steps{
            script{
              send_slack_notification stagename: 'Only-Sync-Backup-Server-from-Prod-Server'
              echo "===========================================\nRUNNING: ${params.REQUESTED_ACTION}\n==========================================="
              echo "==============================\nSTEP 1: Starting Backup Server\n=============================="
              start_backup_server()
              echo "============================================\nSTEP 2:Only Sync of Backup Server from Prod Server\n============================================"
              run_script_on_backup_server scriptname: 'test-2.sh'
              echo "========================="
            }
          }
        }

        stage('Only-Pull-Latest-Code-On-Backup-Server') {
          when {
              expression { params.REQUESTED_ACTION == 'Only-Pull-Latest-Code-On-Backup-Server' }
          }
          steps{
            script{
              send_slack_notification stagename: 'Only-Pull-Latest-Code-On-Backup-Server'
              echo "===========================================\nRUNNING: ${params.REQUESTED_ACTION}\n==========================================="
              run_script_on_backup_server scriptname: 'test-3.sh'
              echo "========================="
            }
          }
        }

        stage('Only-Sync-Database-From-Production-To-Backup-Server') {
          when {
              expression { params.REQUESTED_ACTION == 'Only-Sync-Database-From-Production-To-Backup-Server' }
          }
          steps{
            script{
              send_slack_notification stagename: 'Only-Sync-Database-From-Production-To-Backup-Server'
              echo "===========================================\nRUNNING: ${params.REQUESTED_ACTION}\n==========================================="
              run_script_on_backup_server scriptname: 'test-4.sh'
              echo "========================="
            }
          }
        }

        stage('Start-The-Backup-Server') {
          when {
              expression { params.REQUESTED_ACTION == 'Start-The-Backup-Server' }
          }
          steps{
            script{
              send_slack_notification stagename: 'Start-The-Backup-Server'
              echo "===========================================\nRUNNING: ${params.REQUESTED_ACTION}\n==========================================="
              start_backup_server()
              echo "========================="
            }
          }
        }

        stage('Stop-The-Backup-Server') {
          when {
              expression { params.REQUESTED_ACTION == 'Stop-The-Backup-Server' }
          }
          steps{
            script{
              send_slack_notification stagename: 'Stop-The-Backup-Server'
              echo "===========================================\nRUNNING: ${params.REQUESTED_ACTION}\n==========================================="
              stop_backup_server()
              echo "========================="
            }
          }
        }
    }

    post {

        aborted {

        echo "Sending message to Slack"
        slackSend channel: '#channel-name', color: '#FFC300', message: "ABORTED: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})", teamDomain: 'devops', tokenCredentialId: 'jenkins-slack-credentials-ID'
        }

        failure {

        echo "Sending message to Slack"
        slackSend channel: '#channel-name', color: '#E01563', message: "FAILURE: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})", teamDomain: 'devops', tokenCredentialId: 'jenkins-slack-credentials-ID'
        }

        success {
        echo "Sending message to Slack"
        slackSend channel: '#channel-name', color: '#3EB991', message: "SUCCESS: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})", teamDomain: 'devops', tokenCredentialId: 'jenkins-slack-credentials-ID'
        }
    }
}

def start_backup_server() {
    def myJson = httpRequest url : 'https://api-url.amazonaws.com/', customHeaders: [[name: 'x-api-key', value: 'foobar']]
    def myObject = readJSON text: myJson.content;
    def myObjectres = myObject.toString();
    def coderes = myObject.code.toString();
    if (coderes == "0") {
        echo "SUCCESS"
        echo myObjectres
        echo "WAITING 2m warmup before executing next stage"
        sleep 120
        sh "exit 0"
    } else if (coderes == "2") {
        echo "SUCCESS"
        echo myObjectres
        sh "exit 0"
    } else if (coderes == "1") {
        echo "FAILED"
        echo myObjectres
        sh "exit 1"
    } else {
        echo "FAILED UNKNOWN ERROR"
        echo myObjectres
        sh "exit 1"
    }
}

def run_script_on_backup_server(Map conf) {
  def myJson = httpRequest url : 'https://api-url.amazonaws.com/', customHeaders: [[name: 'x-api-key', value: 'foobar']]
  def myObject = readJSON text: myJson.content;
  def myObjectres = myObject.toString();
  def coderes = myObject.code.toString();
  def messageres = myObject.message.toString();
  if (coderes == "0") {
      echo "SUCCESS"
      echo myObjectres
      sshagent (credentials: ['ID-of-credentials']) {
        sh "ssh -o StrictHostKeyChecking=no ${SSHUSERNAME}@$messageres 'cd ${SCRIPTPATH} && sudo bash ${conf.scriptname} 2>&1'"
      }
      sh "exit 0"
  } else if (coderes == "1") {
      echo "FAILED"
      echo myObjectres
      sh "exit 1"
  } else {
      echo "FAILED UNKNOWN ERROR"
      echo myObjectres
      sh "exit 1"
  }
}

def stop_backup_server() {
    echo "CURRENTLY I AM DOING NOTHING"
}

def send_slack_notification(Map conf) {
    wrap([$class: 'BuildUser']) { script { env.USER_ID = "${BUILD_USER_ID}" } }
    slackSend channel: '#channel-name', color: '#6ECADC', message: "STARTED: Job '${env.JOB_NAME} [${conf.stagename}] [${env.BUILD_NUMBER}] by ${env.USER_ID}' (${env.BUILD_URL})", teamDomain: 'devops', tokenCredentialId: 'jenkins-slack-credentials-ID'
}

// def simple(Map conf) {
//     println "${conf.greeting}, ${conf.username}"
// }
//
// simple username: 'abcd', greeting: 'yoyo'
//https://mrhaki.blogspot.com/2015/09/groovy-goodness-turn-method-parameters.html

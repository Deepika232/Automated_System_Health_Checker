pipeline {
  agent any

  environment {
    IMAGE_NAME = "automated-system-health-checker"
    CONTAINER_NAME = "automated-health-checker"
  }

  stages {
    stage('Clone GitHub repo') {
      steps {
        checkout scm
      }
    }

    stage('Install dependencies') {
      steps {
        sh '''
          python -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Run tests') {
      steps {
        sh '''
          . .venv/bin/activate
          pytest -q
        '''
      }
    }

    stage('Build Docker image') {
      steps {
        sh 'docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} .'
        sh 'docker tag ${IMAGE_NAME}:${BUILD_NUMBER} ${IMAGE_NAME}:latest'
      }
    }

    stage('Run container') {
      steps {
        sh '''
          docker rm -f ${CONTAINER_NAME} || true
          docker run -d --name ${CONTAINER_NAME} -p 5000:5000 ${IMAGE_NAME}:latest
        '''
      }
    }

    stage('Deploy application') {
      steps {
        echo 'Deployment step placeholder (K8s/VM/Compose).'
      }
    }
  }

  post {
    always {
      archiveArtifacts artifacts: 'reports/**, logs/**', allowEmptyArchive: true
    }
  }
}


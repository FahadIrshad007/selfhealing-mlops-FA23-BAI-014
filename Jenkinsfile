pipeline {
    agent any

    environment {
        DOCKERHUB_CREDS = credentials('dockerhub-credentials')
        DOCKER_USER = 'fahadirshad'
        KUBECONFIG = '/var/lib/jenkins/.kube/config'
    }

    stages {
        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t ${DOCKER_USER}/sentiment-api:unstable .
                    docker rm -f sentiment-test-run || true
                    docker run -d --name sentiment-test-run -p 5000:5000 \
                        -v /tmp/app-logs:/app/logs \
                        ${DOCKER_USER}/sentiment-api:unstable
                    sleep 20
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -v ${WORKSPACE}/tests:/tests \
                        -w /tests \
                        python:3.10-slim bash -c "
                            pip install pytest requests -q &&
                            pytest test_api.py -v --tb=short
                        "
                '''
            }
        }

        stage('UI Test') {
            steps {
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        docker run --rm \
                            --network host \
                            -v ${WORKSPACE}/tests:/tests \
                            -w /tests \
                            selenium/standalone-chrome:latest bash -c "
                                pip install selenium pytest requests -q &&
                                pytest test_ui.py -v --tb=short
                            "
                    '''
                }
            }
        }

        stage('Build and Push') {
            steps {
                sh '''
                    echo ${DOCKERHUB_CREDS_PSW} | docker login -u ${DOCKERHUB_CREDS_USR} --password-stdin

                    docker build -t ${DOCKER_USER}/sentiment-api:unstable .
                    docker push ${DOCKER_USER}/sentiment-api:unstable

                    git clone -b stable-fallback https://github.com/FahadIrshad007/selfhealing-mlops-FA23-BAI-014.git stable-build || true
                    if [ -d stable-build ]; then
                        docker build -t ${DOCKER_USER}/sentiment-api:stable stable-build/
                        docker push ${DOCKER_USER}/sentiment-api:stable
                        rm -rf stable-build
                    fi
                '''
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=/var/lib/jenkins/.kube/config
                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml
                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=300s
                    kubectl rollout status deployment/sentiment-green-deployment --timeout=300s
                '''
            }
        }
    }

    post {
        always {
            sh 'docker rm -f sentiment-test-run || true'
        }
    }
}

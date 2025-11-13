// Este é o seu Jenkinsfile
pipeline {
    // 'agent any' = Roda em qualquer "agente" (máquina) disponível
    agent any

    stages {
        // --- Etapa 1: Build Simples (Requisito do Projeto) ---
        stage('1. Build Simulado') {
            steps {
                echo "========================================="
                echo "Iniciando o Build da Vinheria Agnello..."
                // Esta é a linha exata pedida no requisito:
                echo "Deploy da Vinheria"
                echo "Build (simulado) concluído!"
                echo "========================================="
            }
        }

        // --- Etapa 2: Deploy Simulado (Requisito do Projeto) ---
        stage('2. Deploy em Pasta (Simulado)') {
            steps {
                echo "========================================="
                echo "Iniciando Deploy (simulado) em pasta..."

                // Para simular um "deploy em pasta", vamos criar um
                // arquivo de texto simples como se fosse o "pacote" da aplicação
                // A variável "env.BUILD_NUMBER" é fornecida pelo Jenkins
                writeFile file: 'pacote-deploy.txt', text: "Vinheria Agnello - Build #${env.BUILD_NUMBER}"

                // Agora, vamos "arquivar" esse pacote.
                // Isso simula o "deploy em uma pasta de publicação"
                // e o arquivo ficará salvo no Jenkins.
                archiveArtifacts artifacts: 'pacote-deploy.txt'

                echo "Deploy (simulado) concluído com sucesso!"
                echo "========================================="
            }
        }
    }

    // Opcional: Bloco 'post' que roda sempre no final
    post {
        always {
            echo "Pipeline finalizado."
            // Limpa o "workspace" (área de trabalho) para a próxima execução
            cleanWs()
        }
    }
}
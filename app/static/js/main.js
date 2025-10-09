// Main JavaScript file for Client Manager

document.addEventListener('DOMContentLoaded', function() {
    // Enable tooltips everywhere
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Password strength meter for password fields
    const passwordFields = document.querySelectorAll('input[type="password"]');
    passwordFields.forEach(function(field) {
        if (field.id.includes('password') && !field.id.includes('confirm')) {
            field.addEventListener('input', function() {
                const value = field.value;
                let strength = 0;
                
                // Create or find strength meter
                let meterContainer = field.nextElementSibling;
                if (!meterContainer || !meterContainer.classList.contains('password-strength-meter')) {
                    meterContainer = document.createElement('div');
                    meterContainer.className = 'password-strength-meter mt-1';
                    meterContainer.innerHTML = '<div class="progress" style="height: 5px;"><div class="progress-bar" role="progressbar"></div></div><small class="form-text mt-1"></small>';
                    field.insertAdjacentElement('afterend', meterContainer);
                }
                
                const progressBar = meterContainer.querySelector('.progress-bar');
                const text = meterContainer.querySelector('.form-text');
                
                // Calculate password strength
                if (value.length >= 8) strength += 1;
                if (value.match(/[a-z]/) && value.match(/[A-Z]/)) strength += 1;
                if (value.match(/\d/)) strength += 1;
                if (value.match(/[^a-zA-Z0-9]/)) strength += 1;
                
                // Update UI
                let strengthText, strengthClass;
                switch (strength) {
                    case 0:
                    case 1:
                        strengthText = 'Weak';
                        strengthClass = 'bg-danger';
                        progressBar.style.width = '25%';
                        break;
                    case 2:
                        strengthText = 'Fair';
                        strengthClass = 'bg-warning';
                        progressBar.style.width = '50%';
                        break;
                    case 3:
                        strengthText = 'Good';
                        strengthClass = 'bg-info';
                        progressBar.style.width = '75%';
                        break;
                    case 4:
                        strengthText = 'Strong';
                        strengthClass = 'bg-success';
                        progressBar.style.width = '100%';
                        break;
                }
                
                progressBar.className = 'progress-bar ' + strengthClass;
                text.textContent = value.length > 0 ? 'Password strength: ' + strengthText : '';
            });
        }
    });
});
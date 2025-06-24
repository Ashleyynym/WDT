// Phone number formatting and area code selection for edit_profile.html

document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG] phone_format.js loaded');
    const phoneInput = document.getElementById('phone_number');
    const areaCodeSelect = document.getElementById('area_code');
    console.log('[DEBUG] phoneInput:', phoneInput);
    console.log('[DEBUG] areaCodeSelect:', areaCodeSelect);
    if (!phoneInput || !areaCodeSelect) return;

    // Helper: format as (XXX) XXX-XXXX with underscores for missing digits
    function maskPhoneNumber(value) {
        value = value.replace(/\D/g, '');
        let masked = '(___) ___-____';
        let chars = value.split('');
        let result = '';
        let maskIndex = 0;
        for (let i = 0; i < masked.length; i++) {
            if (masked[i] === '_') {
                result += chars[maskIndex] ? chars[maskIndex] : '_';
                maskIndex++;
            } else {
                result += masked[i];
            }
            if (maskIndex >= chars.length) {
                result += masked.slice(i + 1);
                break;
            }
        }
        return result;
    }

    // Show/hide error message
    function setError(msg) {
        let err = document.getElementById('phone-error');
        if (!err) {
            err = document.createElement('div');
            err.id = 'phone-error';
            err.className = 'text-danger mt-1';
            phoneInput.parentNode.appendChild(err);
        }
        err.textContent = msg || '';
        err.style.display = msg ? 'block' : 'none';
    }

    // Format initial value on page load if present
    if (areaCodeSelect.value === 'us') {
        phoneInput.value = maskPhoneNumber(phoneInput.value);
    }

    // Input mask on typing, format as user types, keep cursor position
    phoneInput.addEventListener('input', function(e) {
        if (areaCodeSelect.value === 'us') {
            const start = phoneInput.selectionStart;
            const oldValue = phoneInput.value;
            const formatted = maskPhoneNumber(oldValue);
            phoneInput.value = formatted;
            // Try to keep cursor at the right position
            let newPos = start;
            if (oldValue.length < formatted.length) {
                newPos += formatted.length - oldValue.length;
            } else if (oldValue.length > formatted.length) {
                newPos -= oldValue.length - formatted.length;
            }
            phoneInput.setSelectionRange(newPos, newPos);
        }
        setError('');
    });

    // Validate on blur (only show error, don't reformat)
    phoneInput.addEventListener('blur', function() {
        if (areaCodeSelect.value === 'us') {
            const digits = phoneInput.value.replace(/\D/g, '');
            if (digits.length !== 10) {
                setError('Please enter a valid 10-digit US phone number.');
            } else {
                setError('');
            }
        }
    });

    // Change mask/validation if area code changes (future: add more countries)
    areaCodeSelect.addEventListener('change', function() {
        phoneInput.value = '';
        setError('');
        phoneInput.placeholder = areaCodeSelect.value === 'us' ? '(___) ___-____' : '';
    });
});

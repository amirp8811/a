(function(){
	try {
		document.addEventListener('contextmenu', function(e){ e.preventDefault(); }, { capture:true });
		console.log('%cAnomiDate','color:#9aa3b2');

		// Premium validation UX: add .invalid/.valid classes and custom toasts
		function ensureToastRoot(){
			let root = document.querySelector('.toast-wrap');
			if(!root){
				root = document.createElement('div');
				root.className = 'toast-wrap';
				document.body.appendChild(root);
			}
			return root;
		}
		function showToast(message, type){
			const root = ensureToastRoot();
			const el = document.createElement('div');
			el.className = 'toast ' + (type||'');
			el.textContent = message;
			root.appendChild(el);
			setTimeout(()=>{ el.style.transition='opacity .25s'; el.style.opacity='0'; setTimeout(()=>el.remove(), 250); }, 2400);
		}
		function attachValidation(form){
			if(!form) return;
			form.addEventListener('submit', function(e){
				let firstInvalid = null;
				Array.from(form.querySelectorAll('input,select,textarea')).forEach(function(f){
					if(f.willValidate !== false){
						f.classList.remove('invalid','valid');
						if(!f.checkValidity()){
							f.classList.add('invalid');
							firstInvalid = firstInvalid || f;
						} else {
							f.classList.add('valid');
						}
					}
				});
				if(firstInvalid){
					e.preventDefault();
					showToast(firstInvalid.validationMessage || 'Please fill out this field', 'error');
					firstInvalid.focus();
				}
			});
			Array.from(form.querySelectorAll('input,select,textarea')).forEach(function(f){
				f.addEventListener('input', function(){
					if(f.checkValidity()){
						f.classList.remove('invalid');
						f.classList.add('valid');
					}
				});
			});
		}
		// Attach to all forms on page
		Array.from(document.querySelectorAll('form')).forEach(attachValidation);
	} catch(e) {
		console.warn('init script error', e);
	}
})();

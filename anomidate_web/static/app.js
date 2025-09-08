(function(){
	try {
		document.addEventListener('contextmenu', function(e){ e.preventDefault(); }, { capture:true });
		console.log('%cAnomiDate','color:#9aa3b2');
	} catch(e) {
		console.warn('init script error', e);
	}
})();

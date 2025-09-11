// assets/scroll.js
window.scrollToATM = function(strike) {
    const row = document.querySelector(`[data-strike='${strike}']`);
    if(row) {
        row.scrollIntoView({behavior: 'smooth', block: 'center'});
    }
}

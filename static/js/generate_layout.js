function resetOtherButtons(category) {
    let buttons = document.getElementsByClassName(`${category}-button`);
    for (let button of buttons) {
        button.innerHTML = 'Select';
        button.classList.remove('btn-primary');
        button.classList.add('btn-outline-primary');
        button.disabled = false;
    }
}

function selectTruck(event) {
    let searchParams = currentURL.searchParams;
    searchParams.set('truck', encodeURIComponent(JSON.stringify(event.id)));
    window.location.search = searchParams;

    event.innerHTML = 'Selected';
    event.classList.remove('btn-outline-primary');
    event.classList.add('btn-primary');
    event.disabled = true;
    resetOtherButtons('truck');
}

function selectRacks(event) {
    let checkboxes = document.getElementsByClassName('rack-checkbox');
    let selected_racks = [];
    for (let checkbox of checkboxes) {
        if (checkbox.checked) {
            selected_racks.push(checkbox.id);
        }
    }

    let searchParams = currentURL.searchParams;
    searchParams.set('racks', encodeURIComponent(JSON.stringify(selected_racks)));
    window.location.search = searchParams;
}

function selectManifest(event) {
    let searchParams = currentURL.searchParams;
    searchParams.set('manifest', encodeURIComponent(JSON.stringify(event.id)));
    window.location.search = searchParams;

    event.innerHTML = 'Selected';
    event.classList.remove('btn-outline-primary');
    event.classList.add('btn-primary');
    event.disabled = true;
    resetOtherButtons('manifest');
}

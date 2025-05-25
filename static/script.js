// Import DOM elements
const regexSelect = document.getElementById('regex-select');
const tabs = document.querySelectorAll('.tab');
const graphImage = document.getElementById('graph-image');
const inputString = document.getElementById('input-string');
const validationLog = document.getElementById('validation-log');
const validateButton = document.getElementById('validate-button');
const showPathButton = document.getElementById('show-path-button');
const showFlowButton = document.getElementById('show-flow-button');

// Event listeners
regexSelect.addEventListener('change', (event) => {
    const selectedRegex = event.target.value;
    const activeTab = document.querySelector('.tab.active').getAttribute('data-tab');

    if (!selectedRegex) {
        graphImage.src = "static/placeholder.png";
        return;
    }

    if (activeTab === 'dfa') {
        fetch('/api/draw_dfa', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({regex: selectedRegex, type: activeTab})
        })
        .then(response => response.json())
        .then(data => {
            if (data.image_url) {
                graphImage.src = data.image_url + '.png?t=' + new Date().getTime();
            } else {
                graphImage.src = "static/placeholder.png";
            }
        })
        .catch(() => {
            graphImage.src = "static/placeholder.png";
        });
    } else if (activeTab === 'cfg' || activeTab === 'pda') {
        let imgName = '';
        if (selectedRegex === '(aa+bb+aba+ba)(aba+bab+bbb)(a+b)*(a+b+aa+bba+abab)(aa+bb)*') {
            imgName = activeTab === 'cfg' ? 'cfg_ab' : 'pda_ab';
        } else {
            imgName = activeTab === 'cfg' ? 'cfg_01' : 'pda_01';
        }
        graphImage.src = `/static/${imgName}.png?t=` + new Date().getTime();
    }
    showPathButton.disabled = true;
    showFlowButton.disabled = true;
});

tabs.forEach(tab => {
    tab.addEventListener('click', (event) => {
        tabs.forEach(t => t.classList.remove('active'));
        event.target.classList.add('active');
        const activeTab = event.target.getAttribute('data-tab');
        const selectedRegex = regexSelect.value;

        if (!selectedRegex) {
            graphImage.src = "static/placeholder.png";
            return;
        }

        if (activeTab === 'dfa') {
            fetch('/api/draw_dfa', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({regex: selectedRegex, type: activeTab})
            })
            .then(response => response.json())
            .then(data => {
                if (data.image_url) {
                    graphImage.src = data.image_url + '.png?t=' + new Date().getTime();
                } else {
                    graphImage.src = "static/placeholder.png";
                }
            })
            .catch(() => {
                graphImage.src = "static/placeholder.png";
            });
        } else if (activeTab === 'cfg' || activeTab === 'pda') {
            let imgName = '';
            if (selectedRegex === '(aa+bb+aba+ba)(aba+bab+bbb)(a+b)*(a+b+aa+bba+abab)(aa+bb)*') {
                imgName = activeTab === 'cfg' ? 'cfg_ab' : 'pda_ab';
            } else {
                imgName = activeTab === 'cfg' ? 'cfg_01' : 'pda_01';
            }
            graphImage.src = `/static/${imgName}.png?t=` + new Date().getTime();
        }
    });
});
    
validateButton.addEventListener('click', () => {
    const inputText = inputString.value;
    const selectedRegex = regexSelect.value;

    fetch('/api/validate_dfa', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({regex: selectedRegex, input_string: inputText})
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            validationLog.value += `Error: ${data.error}\n`;
            graphImage.src = "static/placeholder.png";
            // Disable buttons if error
            showPathButton.disabled = true;
            showFlowButton.disabled = true;
            return;
        }
        validationLog.value += `${inputText}: ${data.result}\n`;
        validationLog.scrollTop = validationLog.scrollHeight;

        // Show the animated GIF
        graphImage.src = data.gif_url + '?t=' + new Date().getTime();

        // Enable buttons
        showPathButton.disabled = false;
        showFlowButton.disabled = false;
    })
    .catch(err => {
        validationLog.value += `Error: ${err}\n`;
        graphImage.src = "static/placeholder.png";
        showPathButton.disabled = true;
        showFlowButton.disabled = true;
    });
});

showPathButton.addEventListener('click', () => {
    graphImage.src = '/dfa_frames/dfa_diagram_path.png?t=' + new Date().getTime();
});

showFlowButton.addEventListener('click', () => {
    graphImage.src = '/dfa_frames/dfa_animation.gif?t=' + new Date().getTime();
});
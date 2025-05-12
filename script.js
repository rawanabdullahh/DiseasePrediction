document.addEventListener('DOMContentLoaded', function () {
    const predictButton = document.getElementById('predictButton');
    const symptomsContainer = document.getElementById('symptomsContainer');
    const addSymptomButton = document.getElementById('addSymptom');
    const predictionResults = document.getElementById('predictionResults');
    const symptomList = document.getElementById('symptomList');

    // Fetch available symptoms for autocomplete
    fetch('/symptoms', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    })
        .then(response => response.json())
        .then(data => {
            if (data.symptoms) {
                data.symptoms.forEach(symptom => {
                    const option = document.createElement('option');
                    option.value = symptom;
                    symptomList.appendChild(option);
                });
            }
        })
        .catch(error => {
            console.error('Error fetching symptoms:', error);
            predictionResults.innerHTML = `<div class="alert error">Error loading symptom list: ${error.message}</div>`;
        });

    // Add event listener for adding new symptom input
    if (addSymptomButton) {
        addSymptomButton.addEventListener('click', function () {
            const newSymptomEntry = document.createElement('div');
            newSymptomEntry.classList.add('symptom-entry');
            newSymptomEntry.innerHTML = `
                <input type="text" class="symptom-input" placeholder="Enter a symptom (e.g., cough)" list="symptomList">
                <button class="remove-symptom">Remove</button>
            `;
            symptomsContainer.appendChild(newSymptomEntry);

            newSymptomEntry.querySelector('.remove-symptom').addEventListener('click', function () {
                if (symptomsContainer.querySelectorAll('.symptom-entry').length > 1) {
                    newSymptomEntry.remove();
                }
            });
        });
    }

    // Add event listener for initial remove button
    const initialRemoveButtons = symptomsContainer.querySelectorAll('.remove-symptom');
    initialRemoveButtons.forEach(button => {
        button.style.display = 'block';
        button.addEventListener('click', function () {
            const symptomEntry = button.closest('.symptom-entry');
            if (symptomsContainer.querySelectorAll('.symptom-entry').length > 1) {
                symptomEntry.remove();
            }
        });
    });

    // Add event listener for predict button
    if (predictButton && symptomsContainer) {
        predictButton.addEventListener('click', function () {
            const symptomInputs = symptomsContainer.querySelectorAll('.symptom-input');
            const symptoms = [];
            let hasEmptyInput = false;

            // Collect symptoms and check for empty inputs
            symptomInputs.forEach(input => {
                const symptom = input.value.trim();
                if (symptom) {
                    symptoms.push(symptom);
                } else {
                    hasEmptyInput = true;
                }
            });

            if (hasEmptyInput) {
                predictionResults.innerHTML = '<div class="alert error">Please fill in or remove all empty symptom fields before predicting.</div>';
                return;
            }

            if (symptoms.length === 0) {
                predictionResults.innerHTML = '<div class="alert error">Please enter at least one symptom.</div>';
                return;
            }

            // Show loading message
            predictionResults.innerHTML = '<div class="loading">Analyzing symptoms...</div>';

            // Send symptoms to backend
            fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symptoms: symptoms })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        predictionResults.innerHTML = `<div class="alert error">Error: ${data.error}</div>`;
                    } else {
                        displayDiagnosis(data, symptoms);
                    }
                })
                .catch(error => {
                    predictionResults.innerHTML = `<div class="alert error">Error: ${error.message}</div>`;
                });
        });
    }

    // Function to display diagnosis
    function displayDiagnosis(data, processedSymptoms) {
        let html = `
            <div class="diagnosis-header">
                <h3>Top Predicted Diseases</h3>
                <div class="processed-symptoms">
                    <strong>Based on:</strong> ${processedSymptoms.join(', ')}
                </div>
            </div>
            <div class="predictions-container">
        `;

        data.predictions.forEach(pred => {
            html += `
                <div class="prediction-card">
                    <div class="prediction-header">
                        <div>
                            <h4>${pred.disease}</h4>
                        </div>
                        <div class="probability">${pred.probability}%</div>
                    </div>
                    <div class="probability-bar-container">
                        <div class="probability-bar" style="width: 0%;"></div>
                    </div>
                    <button class="details-button">More Details</button>
                    <div class="prevention-tips">
                        <h5>Prevention Tips</h5>
                        <p>${pred.prevention_tip || 'No prevention tips available.'}</p>
                    </div>
                </div>`;
        });

        html += `</div>`;
        predictionResults.innerHTML = html;

        // Animate probability bars
        document.querySelectorAll('.probability-bar').forEach((bar, index) => {
            if (data.predictions[index]) {
                setTimeout(() => {
                    bar.style.width = `${data.predictions[index].probability}%`;
                }, 100 * index);
            }
        });

        // Add event listeners for details buttons
        document.querySelectorAll('.details-button').forEach(button => {
            button.addEventListener('click', function () {
                const preventionTips = this.nextElementSibling;
                preventionTips.classList.toggle('active');
                this.textContent = preventionTips.classList.contains('active') ? 'Hide Details' : 'More Details';
            });
        });
    }
});
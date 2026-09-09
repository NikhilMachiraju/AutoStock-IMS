console.log("AutoStock Vehicle JavaScript loaded.");

document.addEventListener("DOMContentLoaded", function () {

    const brandSelect = document.getElementById("id_brand");
    const modelSelect = document.getElementById("id_model");
    const variantSelect = document.getElementById("id_variant");

    console.log("Brand select:", brandSelect);
    console.log("Model select:", modelSelect);
    console.log("Variant select:", variantSelect);


    // BRAND CHANGE
    if (brandSelect) {
        brandSelect.addEventListener("change", function () {

            const brandId = this.value;

            console.log("Brand changed:", brandId);

            modelSelect.innerHTML =
                '<option value="">- Select an option -</option>';

            variantSelect.innerHTML =
                '<option value="">- Select an option -</option>';

            if (!brandId) {
                return;
            }

            fetch(`/api/models/${brandId}/`)
                .then(response => response.json())
                .then(data => {

                    console.log("Models loaded:", data);

                    data.forEach(model => {

                        const option = document.createElement("option");

                        option.value = model.id;
                        option.textContent = model.name;

                        modelSelect.appendChild(option);

                    });

                })
                .catch(error => {
                    console.error("Error loading models:", error);
                });

        });
    }


    // MODEL CHANGE
    if (modelSelect) {
        modelSelect.addEventListener("change", function () {

            const modelId = this.value;

            console.log("Model changed:", modelId);

            variantSelect.innerHTML =
                '<option value="">- Select an option -</option>';

            if (!modelId) {
                return;
            }

            fetch(`/api/variants/${modelId}/`)
                .then(response => response.json())
                .then(data => {

                    console.log("Variants loaded:", data);

                    data.forEach(variant => {

                        const option = document.createElement("option");

                        option.value = variant.id;
                        option.textContent = variant.name;

                        variantSelect.appendChild(option);

                    });

                })
                .catch(error => {
                    console.error("Error loading variants:", error);
                });

        });
    }

});
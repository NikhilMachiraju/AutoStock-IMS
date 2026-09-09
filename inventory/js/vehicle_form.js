document.addEventListener("DOMContentLoaded", function () {

    const brandField = document.getElementById("id_brand");
    const modelField = document.getElementById("id_car_model");
    const variantField = document.getElementById("id_vehicle_variant");

    if (!brandField || !modelField || !variantField) {
        console.error("Vehicle dropdown fields not found.");
        return;
    }

    console.log("AutoStock Vehicle JavaScript loaded.");


    function clearField(field) {
        field.innerHTML = "";

        const option = document.createElement("option");
        option.value = "";
        option.textContent = "---------";

        field.appendChild(option);
    }


    function loadModels(brandId) {

        clearField(modelField);
        clearField(variantField);

        if (!brandId) {
            return;
        }

        fetch(`/inventory/api/models/?brand=${brandId}`)
            .then(response => {

                if (!response.ok) {
                    throw new Error("Could not load models.");
                }

                return response.json();
            })
            .then(data => {

                data.models.forEach(model => {

                    const option = document.createElement("option");

                    option.value = model.id;
                    option.textContent = model.name;

                    modelField.appendChild(option);
                });

                console.log("Models loaded:", data.models);

            })
            .catch(error => {
                console.error("Model loading error:", error);
            });
    }


    function loadVariants(modelId) {

        clearField(variantField);

        if (!modelId) {
            return;
        }

        fetch(`/inventory/api/variants/?model=${modelId}`)
            .then(response => {

                if (!response.ok) {
                    throw new Error("Could not load variants.");
                }

                return response.json();
            })
            .then(data => {

                data.variants.forEach(variant => {

                    const option = document.createElement("option");

                    option.value = variant.id;
                    option.textContent = variant.name;

                    variantField.appendChild(option);
                });

                console.log("Variants loaded:", data.variants);

            })
            .catch(error => {
                console.error("Variant loading error:", error);
            });
    }


    brandField.addEventListener("change", function () {

        console.log("Brand changed:", this.value);

        loadModels(this.value);

    });


    modelField.addEventListener("change", function () {

        console.log("Model changed:", this.value);

        loadVariants(this.value);

    });


    // On Add Vehicle page:
    // start with empty Model and Variant fields.
    if (!brandField.value) {
        clearField(modelField);
        clearField(variantField);
    }

});
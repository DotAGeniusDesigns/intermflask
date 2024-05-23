$(document).ready(function() {
    const BASE_URL = '/api/cupcakes';

    async function fetchCupcakes() {
        const response = await axios.get(BASE_URL);
        const cupcakes = response.data.cupcakes;
        $('#cupcake-list').empty();
        cupcakes.forEach(cupcake => {
            $('#cupcake-list').append(`
                <li class="list-group-item">
                    <img src="${cupcake.image}" alt="${cupcake.flavor}" class="img-thumbnail" style="width: 100px; height: 100px;">
                    <b>${cupcake.flavor}</b> (${cupcake.size}) - ${cupcake.rating}/10
                </li>
            `);
        });
    }

    $('#cupcake-form').on('submit', async function(event) {
        event.preventDefault();

        const flavor = $('#flavor').val();
        const size = $('#size').val();
        const rating = $('#rating').val();
        const image = $('#image').val() || 'https://tinyurl.com/demo-cupcake';

        const response = await axios.post(BASE_URL, {
            flavor,
            size,
            rating,
            image
        });

        $('#flavor').val('');
        $('#size').val('');
        $('#rating').val('');
        $('#image').val('');

        fetchCupcakes();
    });

    fetchCupcakes();
});

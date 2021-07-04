// adds another ingredient label and input
function moreIngredients() {
    // counts number of ingredients in form
    let ingredientnumber = $('.ingredient').length;
    ingredientnumber += 1;
    let ingredient = `<label class="ingredient" for="ingredient${ingredientnumber}">Ingredient ${ingredientnumber}:</label>
    <input type="text" name="ingredient${ingredientnumber}"></input>`
    $(ingredient).insertBefore('#moreingredientsbutton');
}
// Makes copy of ingredients section
var $ingredientClone = $('#ingredients').children().clone();
function addIngredient() {
    // adds another ingredient section for user to add another ingredient
    $('#ingredients').append($ingredientClone.slice(0,2))
}

// add recipe button
function addRecipeButton() {
    // shows recipe form
    $('#add-recipe-card').removeClass('hide');
    // hides add recipe button
    $('#add-recipe').addClass('hide');
}

// close button, closes recipe form
function hide() {
    $('#add-recipe-card').addClass('hide');
    $('#add-recipe').removeClass('hide');
}

function moreSteps() {
    $('.more-steps').removeClass('hide');
    $('.more-steps-button').pop();
}
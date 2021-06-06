function addIngredient() {
    var $ingredientClone = $('#ingredients').children().clone();

    $('#ingredients').append($ingredientClone.slice(0,2))
    
}

function addRecipeButton() {
    $('#add-recipe-card').removeClass('hide')
}
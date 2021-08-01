// adds another ingredient label and input
function moreIngredients() {
    // counts number of ingredients in form
    let ingredientnumber = $('.ingredient').length;
    // adds 1 to ingredient number
    ingredientnumber += 1;
    // creates ingredient item
    let ingredient = `<div class="mb-2"><label class="ingredient" for="ingredient${ingredientnumber}">Ingredient ${ingredientnumber}:</label>
    <input class="form-control" type="text" name="ingredient${ingredientnumber}"></input></div>`
    // adds new ingredient item before more ingredient button
    $(ingredient).insertBefore('#moreingredientsbutton');
}

// adds another step label and input
function moresteps() {
    // counts number of steps in form
    let stepnumber = $('.step').length;
    // adds 1 to ingredient number
    stepnumber += 1;
    // creates step item
    let step = `<div class="mb-2"></div><label class="step" for="step${stepnumber}">Step ${stepnumber}:</label>
    <input class="form-control" type="text" name="step${stepnumber}"></input></div>`;
    // adds new step item before more ingredient button
    $(step).insertBefore('#morestepsbutton');
}

// shows edit profile pic form
function showEditPicForm() {
    // hides edit pic button
    $('#show-edit-pic-form').css("display", "none");
    // shows edit pic form
    $('#edit-pic-form').css("display", "block");
}

// shows / hides categories
function showCategories() {
    // toggles visibility of category buttons
    $('#categories').toggle();
}
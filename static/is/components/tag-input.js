// tag-input.js
function updateSelectedTags() {
    // Get the multi-select element
    const select = document.getElementById('tags');
    
    // Get all selected options
    const selectedOptions = Array.from(select.selectedOptions);
    
    // Extract the values of the selected options
    const selectedTags = selectedOptions.map(option => option.value);
    
    // Join the selected tags into a string (comma-separated)
    const selectedTagsString = selectedTags.join(', ');
    
    // Display the selected tags in the input field
    document.getElementById('selectedTags').value = selectedTagsString;
}

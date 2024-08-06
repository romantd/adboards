
function showImageModal(imageUrl) {
    var modalImage = document.getElementById('modalImage');
    modalImage.src = imageUrl;
    $('#imageModal').modal('show');
}

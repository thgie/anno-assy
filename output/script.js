document.addEventListener('DOMContentLoaded', () => {
    document.querySelector('.toggle_comments').addEventListener('click', () => {
        spans = document.querySelectorAll('code > span > span:not(.comment)')
        spans.forEach(el => {
            el.classList.toggle('hide')
        });
    })

    document.querySelector('.toggle_night').addEventListener('click', () => {
        document.querySelector('body').classList.toggle('night')
    })
})
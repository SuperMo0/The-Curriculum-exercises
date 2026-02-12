function fileToDataURL(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

async function handle_submit(e) {
    e.preventDefault();

    try {
        const input = e.target.querySelector('input[type="file"]');
        const file = input?.files?.[0];
        if (!file) return;

        const form = new FormData();
        form.append("image", file);

        const response = await fetch("/upload", {
            method: "POST",
            body: form
        });

        if (!response.ok) {
            throw new Error(`Upload failed: ${response.status}`);
        }

        const data = await response.json();
        const { x_percent, y_percent } = data.analysis;

        console.log(data);

        let mainSubject = document.querySelector('.main_subject')
        mainSubject.textContent = data.main_subject

        let focalPoint = document.querySelector('.focal_point')
        focalPoint.textContent = `Focal Point: X - ${x_percent}%, Y - ${y_percent}%`

        const imageElement = document.querySelector(".output-image");
        if (imageElement) {
            const base64Url = await fileToDataURL(file);
            imageElement.src = base64Url;
            imageElement.style.display = "block";
            imageElement.dataset.xPercent = x_percent;
            imageElement.dataset.yPercent = y_percent;
            imageElement.style.transformOrigin = `${x_percent}% ${y_percent}%`;
        }
    } catch (error) {
        console.error("Error:", error);
    }
}
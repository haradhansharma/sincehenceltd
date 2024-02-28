document.addEventListener("DOMContentLoaded", function () {
    const mouseFollower = document.createElement("div");
    mouseFollower.classList.add("mouse-follower");
    document.body.appendChild(mouseFollower);

    document.addEventListener("mousemove", function (event) {
        const mouseX = event.clientX;
        const mouseY = event.clientY;

        mouseFollower.style.left = mouseX + "px";
        mouseFollower.style.top = mouseY + "px";
    });

    document.querySelectorAll(".target-element").forEach(function (element) {
        element.addEventListener("mouseenter", function () {
            mouseFollower.style.backgroundColor = "#FF0000";
            mouseFollower.style.transform = "scale(10)";
            // mouseFollower.style.filter = "brightness(1.5)";
            
            // mouseFollower.innerHTML = "&#9679;"; 
            mouseFollower.classList.add("add-blend");
           
        });

        element.addEventListener("mouseleave", function () {
            mouseFollower.style.transform = "scale(1)";
            mouseFollower.style.backgroundColor = "var(--bs-primary-rgb-op)";
            // mouseFollower.style.background = "var(--bs-primary-bg-subtle)";
            // mouseFollower.innerHTML = "";
            mouseFollower.classList.remove("add-blend");
        });
    });
   
});

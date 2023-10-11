function main(){
    const blocks = document.getElementsByClassName("block");
    for (const bl of blocks){
        bl.style.position = "absolute";
        bl.style.top = `${Number(bl.getAttribute("data-start")) * 2 + 1}px`
        let length = Number(bl.getAttribute("data-length"))
        bl.style.height = `${length * 2}px`
    }
}

const waitLoad = setInterval(() => {
    if (document.body !== null){
        clearInterval(waitLoad);
        document.body.onload = main()
    }
}, 100)
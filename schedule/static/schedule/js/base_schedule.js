function main(){
    const runs = document.getElementsByClassName("run");
    for (const run of runs){
        console.log("changing ", run)
        run.style.position = "absolute";
        run.style.top = `${Number(run.getAttribute("data-start")) * 2 + 1}px`
        let length = Number(run.getAttribute("data-length"))
        // if (length < 15){
        //     length = 15;
        // }
        run.style.height = `${length * 2}px`
    }
    const interms = document.getElementsByClassName("interm");
    for (const interm of interms){
            console.log("changing ", interm)
            interm.style.position = "absolute";
            interm.style.top = `${Number(interm.getAttribute("data-start")) * 2 + 1}px`
            let length = Number(interm.getAttribute("data-length"))
            // if (length < 15){
            //     length = 15;
            // }
            interm.style.height = `${length * 2}px`
    }
}

const waitLoad = setInterval(() => {
    if (document.body !== null){
        clearInterval(waitLoad);
        document.body.onload = main()
    }
}, 100)
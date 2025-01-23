class PlainTextCountTextarea extends HTMLElement {
    textarea;
    countContainer;
    count = 0;
    conversionEndpoint;
    error;
    abortControllers = [];


    constructor() {
        super();
    }

    connectedCallback() {
        this.conversionEndpoint = this.getAttribute("conversion-endpoint");
        this.setup(0)
    }

    disconnectedCallback() {
        this.textarea.removeEventListener('keyup', this.handleKeyup.bind(this));
        this.textarea.removeEventListener('change', this.handleChange.bind(this));
    }

    renderedCallback() {
        this.textarea = this.querySelector("textarea")

        let countDiv = document.createElement("div");
        this.error = document.createElement("div");

        this.textarea.after(countDiv);
        countDiv.after(this.error);

        this.max = this.getAttribute("max");
        let maxHtmlString = "";

        if (!!this.max) 
        {
            maxHtmlString = ` / ${this.max}`;
        }

        countDiv.innerHTML = `Plain text count: <span>?</span>${maxHtmlString}`;
        

        this.countContainer = countDiv.querySelector("span");

        this.textarea.addEventListener('keyup', this.handleKeyup.bind(this));
        this.textarea.addEventListener('change', this.handleChange.bind(this));

        this.updateCount();
    }

    setup(milliseconds) {
        let failsafe = 5000;

        if (milliseconds > 1000) {
            return;
        }

        window.setTimeout(() => {
            let textarea = this.querySelector("textarea");

            if (!textarea) {
                return this.setup(milliseconds+5);
            }

            this.renderedCallback()

            
        }, milliseconds);
    }

    updateCount = this.debounce(() => {
        console.log('updateCount');
        let abortReason = "newer request";
        while (this.abortControllers.length > 0) {
            this.abortControllers.shift().abort(abortReason);
        }

        let abortController = new AbortController();
        this.abortControllers.push(abortController);

        fetch(this.conversionEndpoint, {
            method: "POST",
            body: JSON.stringify({ "input": this.textarea.value }),
            signal: abortController.signal
        }).then(response => {
            if (!response.ok) {
                throw new Error(`POST Response status: ${response.status}`);
            }

            content = response.json()
            return content
        }).then(content => {
            return fetch(`${this.conversionEndpoint}?id=${content['id']}`, {
                signal: abortController.signal
            });
        }).then(response => {
            if (!response.ok) {
                throw new Error(`GET Response status: ${response.status}`);
            }

            return response.json()
        }).then(content => {
            this.count = content['plain'].length;
            this.countContainer.innerText = this.count;
        }).catch(err => {
            // ignore our own aborted requests
            if (err.name === "AbortError" & err.abortReason === abortReason) {
                return;
            }
            if (err === abortReason) {
                return;
            }

            console.warn({err})
            this.error.innerText = err.message
        });
    }, 300);

    debounce(callback, delay) {
        console.log({ callback, delay });
        let timeout;

        return (...args) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                callback(...args);
            }, delay)
        }
    }

    handleKeyup(e) {
        this.updateCount();
    }

    handleChange(e) {
        this.updateCount();
    }
}

customElements.define('plain-text-count', PlainTextCountTextarea);
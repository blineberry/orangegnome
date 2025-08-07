class PlainTextCountTextarea extends HTMLElement {
    textarea;
    countContainer;
    count = 0;
    conversionEndpoint;
    error;
    abortControllers = [];
    inlineOnly = false;


    constructor() {
        super();
        this.attachShadow({ mode: "open"});
        
        this.shadowRoot.innerHTML = `
            <style>
                pre { text-wrap: wrap; }
            </style>
            <div>
                <div id="markdown">
                    <slot></slot>
                    <div>Count: <span id="markdown-count">?</span></div>
                    <div id="error"></div>
                </div>
                <details id="html">
                    <summary>HTML: <span id="html-count">?</span></summary>
                    <pre><code id="html-content"></code></pre>                    
                </details>
                <details id="plain">
                    <summary>Plain Text: <span id="plain-count">?</span> / <span id="plain-max">?</span></summary>
                    <pre><code id="plain-content"></code></pre>                    
                </details>
            </div>
        `;
    }

    connectedCallback() {
        this.conversionEndpoint = this.getAttribute("conversion-endpoint");
        this.inlineOnly = this.hasAttribute("inline-only");

        if (document.readyState !== 'loading') {
            this.setup();
            return;
        }

        document.addEventListener('DOMContentLoaded', () => this.setup());
    }

    disconnectedCallback() {
        this.textarea.removeEventListener('keyup', this.handleKeyup.bind(this));
        this.textarea.removeEventListener('change', this.handleChange.bind(this));
    }

    setup() {        
        this.textarea = this.querySelector("textarea, input");

        this.htmlCode = this.shadowRoot.querySelector("#html code");
        this.plainCode = this.shadowRoot.querySelector("#plain code");
        this.errorDiv = this.shadowRoot.getElementById("error");

        this.markdownCount = this.shadowRoot.getElementById("markdown-count");
        this.htmlCount = this.shadowRoot.getElementById("html-count");
        this.plainCount = this.shadowRoot.getElementById("plain-count");

        this.shadowRoot.getElementById('plain-max').innerHTML = this.getAttribute("max");

        this.textarea.addEventListener('keyup', this.handleKeyup.bind(this));
        this.textarea.addEventListener('change', this.handleChange.bind(this));
        
        this.updateCount();
    }

    updateContent(content) {
        this.markdownCount.innerText = content.input.length;
        this.htmlCount.innerText = content.html.length;
        this.plainCount.innerText = content.plain.length;

        this.htmlCode.innerText = content.html;
        this.plainCode.innerText = content.plain;
    }

    updateError(errMessage) {
        this.errorDiv.innerText = errMessage;
    }

    updateCount = this.debounce(() => {
        let abortReason = "newer request";
        while (this.abortControllers.length > 0) {
            this.abortControllers.shift().abort(abortReason);
        }

        let abortController = new AbortController();
        this.abortControllers.push(abortController);

        fetch(this.conversionEndpoint, {
            method: "POST",
            body: JSON.stringify({ 
                "input": this.textarea.value, 
                "blockContent": !this.inlineOnly
            }),
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
            console.log(content);

            this.updateContent(content);
            this.updateError("");
        }).catch(err => {
            // ignore our own aborted requests
            if (err.name === "AbortError" & err.abortReason === abortReason) {
                return;
            }
            if (err === abortReason) {
                return;
            }            

            console.warn({err});
            this.updateError(err.message);
            
            if (err.message == "GET Response status: 404") {
                this.updateCount();
            }
        });
    }, 300);

    debounce(callback, delay) {
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
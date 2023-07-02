
function initializeProofs(parent: HTMLElement) {
    parent.querySelectorAll<HTMLElement>(".ui.proof").forEach((proof) => {
        const inners = proof.querySelectorAll<HTMLElement>('.inner > span');
        const explanations = proof.querySelectorAll<HTMLElement>('.explanation span');
        const skipButton = proof.querySelector('.skip');
        const nextButton = proof.querySelector('.next');
        const restartButton = proof.querySelector('.previous');
        explanations.forEach((explanation, inx) => {
            if (inx !== inners.length - 1) { explanation.append(' …'); }
            if (inx !== 0) { explanation.prepend('… '); }
        });
        const update = (index: number) => {
            inners.forEach((inner, inx) => {
                if (inx > index) {
                    inner.style.display = 'none';
                    inner.style.opacity = '0';
                } else {
                    inner.style.display = 'initial';
                    window.requestAnimationFrame(() => inner.style.opacity = '1');
                }
            });
            explanations.forEach((explanation, inx) => {
                if (inx === index) {
                    explanation.style.display = 'block';
                } else {
                    explanation.style.display = 'none';
                }
            });
            proof.dataset.index = index.toString();
            if (index === 0) {
                restartButton?.classList.add('disabled');
            } else {
                restartButton?.classList.remove('disabled');
            }

            if (index === inners.length - 1) {
                skipButton?.classList.add('disabled');
                nextButton?.classList.add('disabled');
                proof.style.cursor = 'auto';
            } else {
                skipButton?.classList.remove('disabled');
                nextButton?.classList.remove('disabled');
                proof.style.cursor = 'pointer';
            }

        }

        const handleNext = (evt: Event) => { evt.stopPropagation(); update(Math.min(inners.length - 1, parseInt(proof.dataset.index || '0', 10) + 1)) };
        const handleRestart = (evt: Event) => { evt.stopPropagation(); update(0); };
        const handleSkip = (evt: Event) => { evt.stopPropagation(); update(inners.length - 1); }

        proof.addEventListener('click', handleNext);
        nextButton?.addEventListener('click', handleNext);
        skipButton?.addEventListener('click', handleSkip);
        restartButton?.addEventListener('click', handleRestart);

        update(0);
    });
}

let sections: HTMLElement[];
let nav: HTMLElement | null;
let current: HTMLElement | null;
function initializeSections() {
    sections = Array.from(document.querySelectorAll<HTMLElement>('section.section')).reverse();
    nav = document.querySelector("nav");
    current = nav?.querySelector('li.current')?.querySelector('a') || null;
}

function initializeDefinitions() {
    document.querySelectorAll('[data-reference]').forEach((ref: HTMLElement) =>{
        const reference = ref.dataset['reference']
        if (reference) {
            const template = (document.getElementById(`ref-${reference}`) as HTMLElement);
            if (template) {
                (window as any).tippy(ref, {
                    content: template.innerHTML,
                    arrow: true,
                    theme: 'light-border',
                    interactive: true,
                    //onShown: () => (window as any).MathJax.typeset(),
                });
            }

        }
    });
}

const PAGES: any = {}
function loadPartialPage(pathname: string) {
    const page = PAGES[pathname];

    const main = document.querySelector('main');
    if (main) {
        main.outerHTML = page;
        window.requestAnimationFrame(init);
    }
}


function linkClick(evt: any) {
    let a = null
    if (evt.target.tagName.toLowerCase() == 'a') {
        a = evt.target;
    } else {
        a = evt.target.closest('a');
    }
    if (!a) return;
    const pathname = a.dataset['pathname'];
    const url = new URL(a.href, window.location.origin)
    console.log(url.pathname, window.location.pathname)
    const isStillSamePage = url.pathname === window.location.pathname || url.pathname === window.location.pathname + 'index.html';
    console.log(isStillSamePage, url.pathname, window.location.pathname);
    if (PAGES[pathname] && !isStillSamePage) {
        evt.preventDefault();
        evt.stopPropagation();
        window.history.pushState({ partial: pathname }, "", a.href);
        loadPartialPage(pathname);
    } else if (isStillSamePage) {
        evt.preventDefault();
        evt.stopPropagation();
        if (url.hash) {
            document.querySelector(url.hash)?.scrollIntoView({behavior:'smooth'});
        } else {
            document.getElementById('top')?.scrollIntoView({behavior:'smooth'});
        }
    }
}

function initializeLinks() {
    document.querySelectorAll('a').forEach((link) => {
        if (link.href.startsWith(window.location.origin)) {
            const url = new URL(link.href, window.location.origin);
            if (url.pathname.endsWith('.html')) {
                url.pathname = url.pathname.replace('.html', '.partial.html')
            } else if (url.pathname.endsWith('/')) {
                url.pathname += 'index.partial.html';
            } else {
                url.pathname += '/index.partial.html';
            }
            if (PAGES[url.pathname] === undefined) {
                PAGES[url.pathname] = null;
                fetch(url.href).then((resp) => resp.text()).then((text) => PAGES[url.pathname] = text);
            }
            link.dataset['pathname'] = url.pathname;
            link.addEventListener('click', linkClick);
        }
    });
}

function updateNavbar() {
    const scrolled = (document.getElementById("scroller")?.scrollTop || 0) + 137;
    const latest = sections.find((section) => section.offsetTop < scrolled);
    let found = false;
    nav?.querySelectorAll('a').forEach((link) => {
        const href = link.getAttribute("href");
        link.classList.remove("active");
        if (href?.includes('#')) {
            const hash = href.split('#').slice(-1)[0];
            if (hash && hash === latest?.id) {
                found = true;
                link.classList.add("active");
            }
        }
    });

    if (!found) {
        current?.classList.add('active');
    } 
}

function toggleNav(setOpen: boolean) {
    if (setOpen && nav) {
        nav.style.display = 'block';
        document.getElementById("menu")?.classList.add('active');
        window.localStorage.setItem('navOpen', 'true');
    } else if (nav) {
        nav.style.display = 'none';
        document.getElementById("menu")?.classList.remove('active');
        window.localStorage.setItem('navOpen', 'false');
    }
}

function init() {
    (window as any).MathJax.typeset();
    const main = document.querySelector('main');
    if (main) { 
        initializeProofs(main);
    }

    nav?.querySelectorAll('li').forEach((li) => {
        const child: any = li.children[0];
        const href = child.href.toString();
        const currentHref = window.location.href.toString().split('#')[0];
        if (child.tagName.toLowerCase() === 'a' && (href === currentHref || ((href + '/') === currentHref))) {
            li.classList.add('current');
        } else {
            li.classList.remove('current');
        }
    });

    initializeSections();
    initializeDefinitions();
    initializeLinks();
    updateNavbar();

    document.querySelector("#scroller")?.addEventListener("scroll", function () {
        window.requestAnimationFrame(updateNavbar);
    });
    if (window?.location?.hash) {
        document.querySelector(window.location.hash)?.scrollIntoView({behavior:'smooth'});
    }
}

window.addEventListener('load', (event) => {
    init();


    document.getElementById("menu")?.addEventListener('click', () => {
        const isOpened = window.localStorage.getItem('navOpen') === 'true';
        toggleNav(!isOpened);
    });
    const isOpened = window.localStorage.getItem('navOpen') === 'true';
    toggleNav(isOpened);



    document.querySelectorAll('nav a').forEach((a) => {
        a.addEventListener("click", updateNavbar);
    });

    window.addEventListener('popstate',(event) => {
        // location.reload()
        console.log(
            `location: ${document.location}, state: ${JSON.stringify(event)}`
        );
    })
});


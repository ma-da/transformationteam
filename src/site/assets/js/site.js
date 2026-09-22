(() => {

  const header =
    document.querySelector(".site-header");

  const courseMenu =
    document.querySelector(".course-menu");

  const welcomeDialog =
    document.querySelector("#welcome-dialog");


  /* ==========================================================
     WELCOME MODAL
     ========================================================== */

  if (welcomeDialog) {

    const openButtons =
      document.querySelectorAll(
        "[data-open-welcome]"
      );

    const closeButton =
      document.querySelector(
        "[data-close-welcome]"
      );


    openButtons.forEach((button) => {

      button.addEventListener(
        "click",
        () => welcomeDialog.showModal()
      );

    });


    closeButton?.addEventListener(
      "click",
      () => welcomeDialog.close()
    );


    welcomeDialog.addEventListener(
      "click",
      (event) => {

        if (event.target === welcomeDialog) {
          welcomeDialog.close();
        }

      }
    );

  }


  /* ==========================================================
     COURSE DROPDOWN
     ========================================================== */

  if (courseMenu) {

    document.addEventListener(
      "click",
      (event) => {

        if (
          courseMenu.open &&
          !courseMenu.contains(event.target)
        ) {
          courseMenu.removeAttribute("open");
        }

      }
    );


    courseMenu
      .querySelectorAll("a")
      .forEach((link) => {

        link.addEventListener(
          "click",
          () => courseMenu.removeAttribute("open")
        );

      });

  }


  /* ==========================================================
     SMART SCROLL HEADER
     ========================================================== */

  if (header) {

    let lastScrollY = window.scrollY;
    let ticking = false;

    const scrollThreshold = 8;
    const topThreshold = 40;


    function updateHeader() {

      const current =
        Math.max(window.scrollY, 0);

      const difference =
        current - lastScrollY;


      if (current <= topThreshold) {

        header.classList.remove(
          "site-header--hidden",
          "site-header--scrolled"
        );

      } else {

        header.classList.add(
          "site-header--scrolled"
        );


        if (
          !courseMenu?.open &&
          Math.abs(difference) >= scrollThreshold
        ) {

          header.classList.toggle(
            "site-header--hidden",
            difference > 0
          );

        }

      }


      lastScrollY = current;
      ticking = false;
    }


    window.addEventListener(
      "scroll",
      () => {

        if (!ticking) {

          requestAnimationFrame(
            updateHeader
          );

          ticking = true;
        }

      },
      { passive: true }
    );

  }

		/* ============================================================
					COSMIC BACKGROUND SCROLLING
					============================================================ */

		const cosmicBackdrop =
				document.querySelector(".cosmic-backdrop");

		const cosmicImage =
				document.querySelector("#cosmic-background");


		if (cosmicBackdrop && cosmicImage) {

				let cosmicTicking = false;


				function updateCosmicBackground() {

						/*
							* Total distance the image can travel before
							* its bottom reaches the bottom of the viewport.
							*/

						const imageHeight =
								cosmicImage.offsetHeight;

						const viewportHeight =
								cosmicBackdrop.clientHeight;

						const maximumTravel = Math.max(
								0,
								imageHeight - viewportHeight
						);


						/*
							* Follow the page's scroll position, but never
							* move the image beyond its own bottom edge.
							*/

						const scrollPosition = Math.max(
								0,
								window.scrollY
						);

						const imageOffset = Math.min(
								scrollPosition,
								maximumTravel
						);


						cosmicImage.style.setProperty(
								"--cosmic-y",
								`${-imageOffset}px`
						);

						cosmicTicking = false;
				}


				/*
					* Limit updates to one per animation frame.
					*/

				function requestCosmicUpdate() {

						if (cosmicTicking) {
								return;
						}

						cosmicTicking = true;

						window.requestAnimationFrame(
								updateCosmicBackground
						);
				}


				window.addEventListener(
						"scroll",
						requestCosmicUpdate,
						{ passive: true }
				);


				/*
					* Recalculate when the viewport changes size,
					* including phone orientation changes.
					*/

				window.addEventListener(
						"resize",
						requestCosmicUpdate
				);


				/*
					* Calculate the initial position, including when
					* a visitor opens a page at a saved scroll position.
					*/

				if (cosmicImage.complete) {

						requestCosmicUpdate();

				} else {

						cosmicImage.addEventListener(
								"load",
								requestCosmicUpdate,
								{ once: true }
						);

				}

		}

})();
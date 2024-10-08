# Informfully Scrapers

![Informfully](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/logo_banner.png)

Welcome to [Informfully](https://informfully.ch/)!
Informfully is an open-source reproducibility platform for content distribution and user experiments.

To view the full documentation, please visit [Informfully at Read the Docs](https://informfully.readthedocs.io/).
It is the combined documentation for all [code repositories](https://github.com/orgs/Informfully/repositories).

**Links and Resources:** [GitHub](https://github.com/orgs/Informfully) | [Website](https://informfully.ch) | [X](https://x.com/informfully) | [Documentation](https://informfully.readthedocs.io) | [DDIS@UZH](https://www.ifi.uzh.ch/en/ddis.html) | [Google Play](https://play.google.com/store/apps/details?id=ch.uzh.ifi.news) | [App Store](https://apps.apple.com/us/app/informfully/id1460234202)

> Note: Our GitHub repositories allow you to run your own instance of Informfully.
If you want to use the Informfully a cloud service, hosted at the University of Zurich, please reach out to us.
Free demo accounts available upon reqeust: info@informfully.ch

## Informfully Preview

![Screenshots](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/informfully_assets/informfully_app_screens.png)

Find out more in the [Online Documentation](https://informfully.readthedocs.io/en/latest/app.html) and create your own instance by deploying the  [Platform Repository](https://github.com/Informfully/Platform).

## Installation Guide

The following installation instructions are an abbreviated version for quickly getting you set and ready. You can access the full [Scrapers documentation here](https://informfully.readthedocs.io/en/latest/scrapers.html).

### Download the Code

```bash
# Download the source code
git clone https://github.com/Informfully/Scrapers.git
```

### Run the Code

Informfully is complemented by a dedicated content scraper.
The entire content scraper pipeline is written in Python and uses MongoDB for persistent storage of news items.
All you need to do is to run add a scraper to [the scraper package](https://github.com/Informfully/Scrapers/tree/main/scraperpackage/scrapers) and call it in *main.py*.
You find sample implementations in this folder as well.

The individual scraper modules (called *scrape.py* or *scrape\_n.py*) are required to implement a scraping function *scrape()*.
There are two main parts to the scraper.
The first part contains the scraper implementations that allow collecting/scraping online resources.
The second part is the processing pipeline for text normalization, cleaning, and subsequent steps before storing them in the database.

![Architecture](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/content_scraper_non-transparent.png)

## Citation

If you use any code or data of this repository in a scientific publication, we ask you to cite the following papers:

<!--Update once the final version of the paper has been published.-->

- [Informfully - Research Platform for Reproducible User Studies](https://dl.acm.org/doi/10.1145/3640457.3688066), Heitz *et al.*, Proceedings of the 18th ACM Conference on Recommender Systems, 2024.

  ```
  @inproceedings{heitz2024informfully,
    title={Informfully - Research Platform for Reproducible User Studies},
    author={Heitz, Lucien and Croci, Julian A and Sachdeva, Madhav and Bernstein, Abraham},
    booktitle={Proceedings of the 18th ACM Conference on Recommender Systems},
    pages={660--669},
    year={2024}
  }
  ```

- [Deliberative Diversity for News Recommendations - Operationalization and Experimental User Study](https://dl.acm.org/doi/10.1145/3604915.3608834), Heitz *et al.*, Proceedings of the 17th ACM Conference on Recommender Systems, 813–819, 2023.

  ```
  @inproceedings{heitz2023deliberative,
    title={Deliberative Diversity for News Recommendations: Operationalization and Experimental User Study},
    author={Heitz, Lucien and Lischka, Juliane A and Abdullah, Rana and Laugwitz, Laura and Meyer, Hendrik and Bernstein, Abraham},
    booktitle={Proceedings of the 17th ACM Conference on Recommender Systems},
    pages={813--819},
    year={2023}
  }
  ```

- [Benefits of Diverse News Recommendations for Democracy: A User Study](https://www.tandfonline.com/doi/full/10.1080/21670811.2021.2021804), Heitz *et al.*, Digital Journalism, 10(10): 1710–1730, 2022.

  ```
  @article{heitz2022benefits,
    title={Benefits of diverse news recommendations for democracy: A user study},
    author={Heitz, Lucien and Lischka, Juliane A and Birrer, Alena and Paudel, Bibek and Tolmeijer, Suzanne and Laugwitz, Laura and Bernstein, Abraham},
    journal={Digital Journalism},
    volume={10},
    number={10},
    pages={1710--1730},
    year={2022},
    publisher={Taylor \& Francis}
  }
  ```

## Contributing

Your are welcome to contribute to the Informfully ecosystem and become a part of our community. Feel free to:
  - fork any of the [Informfully repositories](https://github.com/Informfully)
  - join and write on the [dicussion board](https://github.com/orgs/Informfully/discussions)
  - make changes and create pull requests

Please post your feature requests and bug reports in our [GitHub issues](https://github.com/Informfully/Documentation/issues) section.

## License

Released under the [MIT License](LICENSE). (Please note that the respective copyright licenses of third-party libraries and dependencies apply.)

![Screenshots](https://raw.githubusercontent.com/Informfully/Documentation/main/docs/source/img/app_screens.png)

# Informfully Scrapers

![Informfully](https://informfully.readthedocs.io/en/latest/_images/logo_banner.png)

Welcome to the [Informfully](https://informfully.ch/)! Informfully is a open-source reproducibility platform for content distribution and user experiments from the [University of Zurich](https://www.ifi.uzh.ch/en.html).

To view the documentation, please visit [Informfully at Read the Docs](https://informfully.readthedocs.io/). It is the combined documentation for all [code repositories](https://github.com/orgs/Informfully/repositories).

**Links and Resources:** [Website](https://informfully.ch/) | [Documentation](https://informfully.readthedocs.io/) | [Informfully](https://github.com/orgs/Informfully/repositories) | [DDIS@UZH](https://www.ifi.uzh.ch/en/ddis.html)

## Installation

The following installation instructions are an abbreviated version for quickly getting you set and ready. You can access full the [Scrapers documentation here](https://informfully.readthedocs.io/en/latest/scrapers.html).

### Download the Code

```bash
# Download the source code
git clone https://github.com/Informfully/Scrapers.git
```

### Run the Code

Informfully is complemented by a dedicated content scraper.
The entire content scraper pipeline is written in Python and uses MongoDB for persistent storage of news items.
All you need to do is to run add a scraper to [the scraper package](https://github.com/Informfully/Scrapers/tree/main/scraperpackage/scrapers>) and call it in `main.py`.
You find sample implementations in this folder as well.

The individual scraper modules (called `scrape.py` or `scrape\_n.py`) are required to implement a scraping function `scrape()`.
There are two main parts to the scraper.
The first part contains the scraper implementations that allow collecting/scraping online resources.
The second part is the processing pipeline for text normalization, cleaning, and subsequent steps before storing them in the database.

![Architecture](https://informfully.readthedocs.io/en/latest/_images/content_scraper.png)

## Citation
If you use any Informfully code/repository in a scientific publication, we ask you to cite the following papers:

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
Your are welcome to contribute to the Informfully ecosystem and become a part of your cummunity. Feel free to:
  - fork any of the [Informfully repositories](https://github.com/Informfully/Documentation) and
  - make changes and create pull requests.

Please post your feature requests and bug reports in our [GitHub issues](https://github.com/Informfully/Documentation/issues) section.

## License
Released under the [MIT License](LICENSE). (Please note that the respective copyright licenses of third-party libraries and dependencies apply.)

![Screenshots](https://informfully.readthedocs.io/en/latest/_images/app_screens.png)

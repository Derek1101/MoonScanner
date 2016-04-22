                // MoonScanner //

        Simple tool to scann broken links (site, image).

    ~ Support
        check broken link
        generate both good link and bad link report

    ~ How to
        Please install **beautifulsoup4** first:

            ```python
                pip install beautifulsoup4
            ```

        Add urls to sites.txt

        Run command

            ```python
                python MoonScanner.py
            ```
        Two reports: good.txt and bad.txt, including detailed info.

    ~ Issue
        Inner link support, such as 'http://wacn.ppe.chinaclouds.cn/documentation/articles/virtual-machine-deploy#Step2', currently we just ignore inner link, but it should proivde better solution to this.
        Performance is not fast as imagined, I've test 3 sites, average time for check one page is about 6s~10s.

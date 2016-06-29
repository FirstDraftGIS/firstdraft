Feature: News Articles
    In order to check to make sure First Draft works with links to news articles

    Scenario Outline: Check BBC News Article on Libya
        When we start with a link to <url>
         And after we wait for 120 seconds
        Then we should see a map

        Examples: urls
            | url |
            | www.bbc.com/news/world-middle-east-19744533 |

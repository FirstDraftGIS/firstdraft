Feature: Links to Files
    In order to check to make sure First Draft works with links to files

    Scenario Outline: Check PDF Report
        When user enters a link to a file at <url>
        Then we should see a map after a while

        Examples: urls
            | url |
            | https://www.state.gov/documents/organization/245365.pdf |

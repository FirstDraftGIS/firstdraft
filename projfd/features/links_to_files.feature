Feature: Links to Files
    In order to check to make sure First Draft works with links to files

    Scenario Outline: Check PDF Report
        When user enters a link to a file at <url>
         And after we wait for 120 seconds
        Then we should see a map

        Examples: urls
            | url |
            | https://www.state.gov/documents/organization/245365.pdf |

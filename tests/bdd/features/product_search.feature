
Feature: Product Search

  As a customer
  I want to search for products by keyword
  So that I can find the tools I need

  Scenario Outline: Search for existing products
    Given the customer is viewing the product catalog
    When the customer searches for "<keyword>"
    Then the search results include products matching "<expected_keyword>"

    Examples:
      | keyword | expected_keyword |
      | pliers  | pliers           |
      | hammer  | hammer           |
      | saw     | saw              |

  Scenario: Search for a product that does not exist
    Given the customer is viewing the product catalog
    When the customer searches for "zzz-no-such-tool"
    Then the customer sees a message that no products were found

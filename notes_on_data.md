## Structure

- XML
- hierarchical
- indentation to show nesting levels

## Root tag

- `<PubmedArticleSet>`
- encapsulates multiple `<PubmedArticle>` tags. Each `<PubmedArticle>` tag represents a single article with its associated metadata.

## Data stored with each Article

- `<PubmedArticle>` tag contains data related to a scientific article, including details like PMID (PubMed ID), date revised, journal information, article title, abstract, author list, publication type, etc

## Data stored with each Author

- `<Author>` tag within an `<AuthorList>` tag contains data about an author, including their last name, first name, initials, and affiliation information

## How to find author's affiliated institution?

- look for the `<Affiliation>` tag within the `<AffiliationInfo>` tag inside the respective `<Author>` tag

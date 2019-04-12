// NewsPanel.js
import './NewsPanel.css';
import React from 'react'
import NewsCard from '../NewsCard/NewsCard';

class NewsPanel extends React.Component {
  constructor() {
    super();
    this.state = {news: null};
  }
  componentDidMount() {
    this.loadMoreNews();
  }
  loadMoreNews() {
    this.setState({
      news: [
        {
          "srouce": "The Wall Street Journal",
          "title": "Berkshire",
          "description": "Berkshire posted a Berkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted a",
          "url": "https:",
          "utlToImage": "",
          "publishedAt": "2018-02-",
          "digest": "3Rju",
          "reason": "Recommend"
        },
        {
          "srouce": "The Wall Street Journal",
          "title": "Berkshire",
          "description": "Berkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted aBerkshire posted a",
          "url": "https:",
          "utlToImage": "",
          "publishedAt": "2018-02-",
          "digest": "3Rju",
          "reason": "Recommend"
        }
      ]
    });
  }
  renderNews() {
    const news_list = this.state.news.map(news => {
      return (
        <a className = 'list-group-item' key = {news.digest} href = '#'>
          <NewsCard news = {news} />
        </a>
      );
    });

    return (
      <div className = 'container-fluid'>
        <div className = 'list-group'>
          {news_list}
        </div>
      </div>
    );
  }
  render() {
    if (!this.state.news) {
      return (
        <div>
          Loading...
        </div>
      );
    } else {
      return (
        <div>
          {this.renderNews()}
        </div>
      );
    }
  }
}

export default NewsPanel;
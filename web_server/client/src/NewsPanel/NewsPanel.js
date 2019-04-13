// NewsPanel.js
import './NewsPanel.css';
import React from 'react'
import NewsCard from '../NewsCard/NewsCard';
import _ from 'lodash';

class NewsPanel extends React.Component {
  constructor() {
    super();
    this.state = {news: null};
  }
  componentDidMount() {
    this.loadMoreNews();
    this.loadMoreNews = _.debounce(this.loadMoreNews, 1000);
    window.addEventListener('scroll', () => this.handleScroll());
  }
  handleScroll() {
    let scrollY = window.scrollY 
               || window.pageYOffset 
               || window.documentElement.scrollTop;
    if ( (window.innerHeight + scrollY) >= (document.body.offsetHeight - 50) ) {
      console.log('Loading more news...');
      this.loadMoreNews();
    }
  }
  loadMoreNews() {
    const news_url = 'http://' + window.location.hostname + ':3000' + '/news';
    const request = new Request(news_url, {method: 'GET'});
    fetch(request)
      .then(res => res.json())
      .then(news_list => {
        this.setState({
          news: this.state.news ? this.state.news.concat(news_list) : news_list,
        });
      })
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
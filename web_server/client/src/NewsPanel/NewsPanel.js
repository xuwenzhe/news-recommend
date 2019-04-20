// NewsPanel.js
import './NewsPanel.css';
import React from 'react'
import NewsCard from '../NewsCard/NewsCard';
import Auth from '../Auth/Auth';
import _ from 'lodash';

class NewsPanel extends React.Component {
  constructor() {
    super();
    this.state = {news: null, pageNum: 1, loadedAll: false};
  } 

  // componentDidMount() gets called automatically after constructor finishes.
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
    console.log('Actually triggered loading more news.')
    if (this.state.loadedAll == true) {
      return;
    }

    // refer to newsAPI at web_server/server/routes/news.js
    const news_url = 'http://' + window.location.hostname
                   + ':3000/news/userId=' + Auth.getEmail()
                   + "&pageNum=" + this.state.pageNum;

    // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/encodeURI
    const request = new Request(encodeURI(news_url), {
      method: 'GET',
      headers: {
        'Authorization': 'bearer ' + Auth.getToken(),
      },
    });

    fetch(request)
      .then(res => res.json())
      .then(news_list => {
        // render-cycle explanation
        // https://stackoverflow.com/a/24719289
        if (!news_list || news_list.length == 0) {
          this.setState({loadedAll:true});
        }
        this.setState({
          news: this.state.news ? this.state.news.concat(news_list) : news_list,
          pageNum: this.state.pageNum + 1
        });
      })
  }
  renderNews() {
    const news_list = this.state.news.map(news => {
      // passes a property `news` when adding <NewsCard/>
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
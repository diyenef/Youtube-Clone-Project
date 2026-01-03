document.addEventListener('DOMContentLoaded', function(){
  const menuBtn = document.querySelector('.menu-btn');
  const sidebar = document.querySelector('.sidebar');
  if(menuBtn && sidebar){
    menuBtn.addEventListener('click', function(){
      sidebar.classList.toggle('open');
    });
  }

  // Simple placeholder: close sidebar on content click for small screens
  const content = document.querySelector('.content');
  if(content && sidebar){
    content.addEventListener('click', function(){
      if(window.innerWidth < 1100){
        sidebar.classList.remove('open');
      }
    });
  }

  // CSRF helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  const csrftoken = getCookie('csrftoken');

  // derive video id for this page from any element that exposes it
  const pageVideoEl = document.querySelector('[data-video-id]');
  const pageVideoId = pageVideoEl ? pageVideoEl.dataset.videoId : null;

  // Like button AJAX
  const likeBtn = document.getElementById('like-btn');
  if(likeBtn){
    likeBtn.addEventListener('click', function(e){
      e.preventDefault();
      const videoId = this.dataset.videoId;
      // optimistic UI: toggle immediately
      const countEl = document.getElementById('like-count');
      const prevLiked = this.dataset.liked === '1';
      const prevCount = parseInt(countEl.textContent || '0', 10);
      const newLiked = !prevLiked;
      const newCount = newLiked ? prevCount + 1 : Math.max(prevCount - 1, 0);

      // apply optimistic UI
      this.dataset.liked = newLiked ? '1' : '0';
      this.classList.add('loading');
      this.innerHTML = (newLiked ? 'Unlike' : 'Like') + ' (<span id="like-count">' + newCount + '</span>)';
      // add spinner to show background activity
      const spinner = document.createElement('span');
      spinner.className = 'spinner';
      this.appendChild(spinner);

      // send request
      fetch(`/video/${videoId}/like_ajax/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        }
      }).then(async res => {
        if(!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        // apply authoritative state
        countEl.textContent = data.count;
        likeBtn.dataset.liked = data.liked ? '1' : '0';
        likeBtn.innerHTML = (data.liked ? 'Unlike' : 'Like') + ' (<span id="like-count">' + data.count + '</span>)';
      }).catch(err => {
        console.error(err);
        // rollback optimistic UI
        likeBtn.dataset.liked = prevLiked ? '1' : '0';
        countEl.textContent = prevCount;
        likeBtn.innerHTML = (prevLiked ? 'Unlike' : 'Like') + ' (<span id="like-count">' + prevCount + '</span>)';
        // show inline error
        const errorNotice = document.createElement('div');
        errorNotice.className = 'inline-error';
        errorNotice.textContent = 'Could not update like — try again.';
        likeBtn.parentNode.appendChild(errorNotice);
        setTimeout(() => errorNotice.remove(), 4000);
      }).finally(() => {
        // remove spinner if still present
        if (spinner && spinner.parentNode) spinner.parentNode.removeChild(spinner);
        likeBtn.classList.remove('loading');
      });
    });
  }

  // Comment form AJAX
  const commentForm = document.getElementById('comment-form');
  if(commentForm){
    // allow replying: listen for reply-btn clicks to open a small inline reply form
    document.addEventListener('click', function(e){
      const replyBtn = e.target.closest('.reply-btn');
      if(replyBtn){
        const parentId = replyBtn.dataset.parentId;
        // if a reply form already exists under this comment, focus it
        const parentEl = document.querySelector(`.comment[data-comment-id="${parentId}"]`);
        if(!parentEl) return;
        // remove any existing temporary reply forms
        const existing = document.querySelector('.inline-reply-form');
        if(existing) existing.remove();
        const form = document.createElement('form');
        form.className = 'inline-reply-form';
        form.innerHTML = `<textarea name="text" rows="2" placeholder="Add a public reply..."></textarea><div><button class="btn" type="submit">Reply</button> <button type="button" class="btn cancel-reply">Cancel</button></div>`;
        parentEl.appendChild(form);
        const textarea = form.querySelector('textarea');
        textarea.focus();

        // handle cancel
        form.querySelector('.cancel-reply').addEventListener('click', function(){ form.remove(); });

        // handle submit via AJAX reusing comment endpoint with parent id
        form.addEventListener('submit', function(ev){
          ev.preventDefault();
          const text = textarea.value.trim();
          if(!text) return;
          // optimistic placeholder as reply
          const repliesContainer = parentEl.querySelector('.replies') || parentEl;
          const placeholder = document.createElement('div');
          placeholder.className = 'comment reply placeholder';
          placeholder.innerHTML = `<strong>${(window.USERNAME||'You')}</strong> - <em>Posting...</em>`;
          repliesContainer.insertBefore(placeholder, repliesContainer.firstChild);
          textarea.disabled = true;

            const videoIdForReply = pageVideoId || (likeBtn ? likeBtn.dataset.videoId : null);
            fetch(`/video/${videoIdForReply}/comment_ajax/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'X-CSRFToken': csrftoken,
              'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({text: text, parent: parentId})
          }).then(r => { if(!r.ok) throw new Error('Network response not ok'); return r.json(); })
            .then(data => {
              placeholder.classList.remove('placeholder');
              placeholder.setAttribute('data-comment-id', data.id);
              placeholder.innerHTML = `<strong>${data.author}</strong> - ${data.text}`;
              placeholder.classList.add('fade-in');
              form.remove();
            }).catch(err => {
              console.error(err);
              placeholder.remove();
              const errorNotice = document.createElement('div');
              errorNotice.className = 'inline-error';
              errorNotice.textContent = 'Could not post reply — try again.';
              parentEl.appendChild(errorNotice);
              setTimeout(()=>errorNotice.remove(),4000);
            }).finally(()=>{ textarea.disabled = false; });
        });
      }
    });

    commentForm.addEventListener('submit', function(e){
      e.preventDefault();
      const textEl = commentForm.querySelector('textarea, input[name="text"]');
      if(!textEl) return;
      const text = textEl.value.trim();
      if(!text) return;
      const videoId = pageVideoId || (likeBtn ? likeBtn.dataset.videoId : null);
      if(!videoId) return;

      // create optimistic placeholder
      const list = document.getElementById('comments-list');
      const placeholder = document.createElement('div');
      placeholder.className = 'comment placeholder';
      placeholder.innerHTML = `<strong>${(window.USERNAME||'You')}</strong> - <em>Posting...</em>`;
      list.insertBefore(placeholder, list.firstChild);

      // disable input/button while posting
      const submitBtn = commentForm.querySelector('button[type="submit"]');
      textEl.disabled = true;
      if(submitBtn) submitBtn.disabled = true;

      fetch(`/video/${videoId}/comment_ajax/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
          'X-Requested-With': 'XMLHttpRequest'
        },
        body: JSON.stringify({text: text})
      }).then(r => {
        if(!r.ok) throw new Error('Network response was not ok');
        return r.json();
      }).then(data => {
        // replace placeholder with authoritative comment and animate
          placeholder.classList.remove('placeholder');
          placeholder.setAttribute('data-comment-id', data.id);
          placeholder.innerHTML = `<strong>${data.author}</strong> - ${data.text}`;
          // add fade-in animation
          placeholder.classList.add('fade-in');
          // clear input
          textEl.value = '';
      }).catch(err => {
        console.error(err);
        // remove placeholder and show error
        placeholder.remove();
        const errorNotice = document.createElement('div');
        errorNotice.className = 'inline-error';
        errorNotice.textContent = 'Could not post comment — try again.';
        commentForm.parentNode.insertBefore(errorNotice, commentForm);
        setTimeout(() => errorNotice.remove(), 4000);
      }).finally(() => {
        textEl.disabled = false;
        if(submitBtn) submitBtn.disabled = false;
      });
    });
  }

  // Flag comment AJAX handling
  document.addEventListener('click', function(e){
    const flagBtn = e.target.closest('.flag-btn');
    if(!flagBtn) return;
    const commentId = flagBtn.dataset.commentId;
    if(!commentId) return;
    const videoIdForFlag = pageVideoId || (likeBtn ? likeBtn.dataset.videoId : null);
    fetch(`/video/${videoIdForFlag}/comment_flag_ajax/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken, 'X-Requested-With': 'XMLHttpRequest' },
      body: JSON.stringify({comment_id: commentId})
    }).then(r => { if(!r.ok) throw new Error('Network response not ok'); return r.json(); }).then(data=>{
      flagBtn.textContent = 'Flagged';
      flagBtn.disabled = true;
    }).catch(err=>{
      console.error(err);
      const errorNotice = document.createElement('div');
      errorNotice.className = 'inline-error';
      errorNotice.textContent = 'Could not flag — try again.';
      flagBtn.parentNode.appendChild(errorNotice);
      setTimeout(()=>errorNotice.remove(),4000);
    });
  });
  
  // Shorts preview autoplay using IntersectionObserver (muted). Also show play icon and duration overlay.
  (function setupShortsAutoplay(){
    const videos = Array.from(document.querySelectorAll('.short-preview'));
    if(!videos.length) return;

    // create overlays for each short card
    videos.forEach(video => {
      const card = video.closest('.short-card');
      if(!card) return;
      // overlay container
      let overlay = card.querySelector('.short-overlay');
      if(!overlay){
        overlay = document.createElement('div');
        overlay.className = 'short-overlay';
        overlay.innerHTML = '<span class="short-play">▶</span><span class="short-duration">0:00</span>';
        card.appendChild(overlay);
      }

      // when metadata is loaded, show duration
      video.addEventListener('loadedmetadata', () => {
        const dur = Math.floor(video.duration || 0);
        const m = Math.floor(dur/60); const s = dur % 60;
        const label = `${m}:${s.toString().padStart(2,'0')}`;
        const durEl = card.querySelector('.short-duration');
        if(durEl) durEl.textContent = label;
        video.dataset.duration = label;
      });
    });

    const options = { root: null, rootMargin: '0px', threshold: [0.5] };
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        const vid = entry.target;
        const card = vid.closest('.short-card');
        if(!card) return;
        const overlay = card.querySelector('.short-overlay');
        if(entry.intersectionRatio >= 0.5){
          // play muted preview
          try{ vid.muted = true; vid.play(); if(overlay) overlay.classList.add('playing'); }catch(e){}
        } else {
          try{ vid.pause(); vid.currentTime = 0; if(overlay) overlay.classList.remove('playing'); }catch(e){}
        }
      });
    }, options);

    videos.forEach(v => {
      // ensure video is muted to allow autoplay
      try{ v.muted = true; }catch(e){}
      observer.observe(v);
      // clicking the card should navigate; pause preview before navigation
      const card = v.closest('.short-card');
      if(card){
        card.addEventListener('click', (ev) => {
          try{ v.pause(); }catch(e){}
        });
      }
    });
  })();
});

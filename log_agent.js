async function logToGitHub(message) {  
  const owner = process.env.GITHUB_OWNER;  
  const repo = process.env.GITHUB_REPO;  
  const token = process.env.GITHUB_TOKEN;  
  const date = new Date().toISOString().split('T')[0];  
  const path = `logs/${date}.txt`;  

  let sha = null;  
  let currentContent = '';  

  try {  
    const getRes = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}`, {  
      headers: {  
        'Authorization': `token ${token}`,  
        'Accept': 'application/vnd.github.v3+json'  
      }  
    });  
    if (getRes.status === 200) {  
      const data = await getRes.json();  
      sha = data.sha;  
      currentContent = atob(data.content.replace(/\n/g, ''));  
    } else if (getRes.status !== 404) {  
      throw new Error(`GitHub get error: ${getRes.status}`);  
    }  
  } catch (e) {  
    console.error('Get log error:', e);  
  }  

  const newContent = currentContent ? currentContent + '\n' + new Date().toISOString() + ' ' + message : new Date().toISOString() + ' ' + message;  
  const base64Content = btoa(newContent);  

  const body = {  
    message: 'Append NovaOS log',  
    content: base64Content  
  };  
  if (sha) {  
    body.sha = sha;  
  }  

  try {  
    const putRes = await fetch(`https://api.github.com/repos/${owner}/${repo}/contents/${path}`, {  
      method: 'PUT',  
      headers: {  
        'Authorization': `token ${token}`,  
        'Accept': 'application/vnd.github.v3+json'  
      },  
      body: JSON.stringify(body)  
    });  
    if (!putRes.ok) {  
      throw new Error(`GitHub put error: ${putRes.status}`);  
    }  
  } catch (e) {  
    console.error('Log error:', e);  
  }  
}  

// Example call - adjust for your agents  
async function main() {  
  await logToGitHub('Test log message');  
  console.log('Logged to GitHub');  
}  

main();  

for repo in `awk 'NR>=3 { print $2 }' firstdraft/system_repositories.md `
do
  add-apt-repository -y $repo;
done
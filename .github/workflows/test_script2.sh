echo "Hello"
echo "$1"
if [[ -z $1 || $1=="" ]]; then
	echo "PR is empty";
else
	# Pull Requests can't use git branch, so Github provides it for us
	echo "PR has something";
	echo "$1";
fi
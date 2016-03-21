var kabarakApp = angular.module("KabarakApp", []);
/**
 * COnfigur angular to prevent conflicts with jinja by changing expression symbols
 */
kabarakApp.config(['$interpolateProvider', function ($interpolateProvider) {
	$interpolateProvider.startSymbol('{[');
	$interpolateProvider.endSymbol(']}');
}]);

/**
 * Custom service to login user
 */
kabarakApp.factory("sendlogin", ["$http", "$q", function ($http, $q) {
	var util_login = {
		postData: function (data) {
			return $q(function (resolve, reject) {
				$http({
					method: "POST"
					, url: "/login_authenticate"
					, headers: {
						"Content-Type": "x-www-form-urlencoded"
					}
					, data: {
						username: data.username
						, password: data.password
					}
				}).then(function success(response) {
					console.warn(response.data)
					if (response.data.error !== undefined) {
						console.error(response.data.error);
						reject(response)
					}
					resolve(response);
				}, function failure(response) {
					// Using double equals comparison becau
					if (response.data == undefined) {
						response.data = {
							error: "Connection problem, couldn't reach the server! Try again later."
						};
						reject(response);
					}
					console.error(response);
					reject(response);
				});

			});
		}


	}
	return util_login;



}]);


kabarakApp.controller("loginCTRL", ["$scope", "$window", "sendlogin", function ($scope, $window, sendlogin) {
	$scope.user = {};
	$scope.messages = {};
	$scope.toggleError = function () {
		$scope.messages.error = false;
	};


	$scope.loginFunction = function () {
		var promise = sendlogin.postData($scope.user);
		promise.then(function success(response) {
			console.log(response.data)
			$scope.user = response.data;
			console.log($scope.user);
			$window.location.href = "/home";
		}, function failed(response) {
			console.warn(response)
			$scope.messages = {
				alert: response.data.error
				, error: true
			}
		});
	};

}]);
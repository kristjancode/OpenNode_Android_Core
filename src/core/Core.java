package core;

import core.network.ServerConnector;
import core.interfaces.ComputeManager;
import core.interfaces.NetworkManager;

public class Core 
{
	public Core()
	{
		m_serverConnector = new ServerConnector("localhost", 8080);
		m_computeManager = new ComputeManager(this);
		m_networkManager = new NetworkManager(this);
	}
	
	public ServerConnector serverConnector()
	{
		return m_serverConnector;
	}
	
	public ComputeManager computeManager()
	{
		return m_computeManager;
	}
	
	public NetworkManager networkManager()
	{
		return m_networkManager;
	}
	
	private ServerConnector m_serverConnector;
	private ComputeManager m_computeManager;
	private NetworkManager m_networkManager;
}